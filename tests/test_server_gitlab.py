import io
import zipfile
import pytest
import aiohttp
import responses
import aioresponses

from flexmock import flexmock

from logdetective.server.server import process_gitlab_job_event
from logdetective.server.models import JobHook
from logdetective.server import server


@pytest.fixture
def mock_config():
    flexmock(server).should_receive("SERVER_CONFIG").and_return(
        flexmock(
            gitlab=flexmock(
                api_url="https://gitlab.com", api_token="abc", max_artifact_size=1234567
            ),
            extractor=flexmock(max_clusters=1),
            inference=flexmock(
                model="some.gguf",
                max_tokens=-1,
                api_token="def",
                api_endpoint="/chat/completitions",
                temperature=1,
                url="http://llama-cpp-server:8000",
            ),
            general=flexmock(packages="a package"),
        )
    )


def create_zip_content(filepath) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(filepath + "task_failed.log", "root.log")
        zip_file.writestr(filepath + "root.log", "ERROR: some sort of error")

    zip_buffer.seek(0)
    return zip_buffer.read()


@pytest.fixture
def mock_job_hook():
    job_hook = JobHook(
        object_kind="build",
        build_id=123,
        pipeline_id=456,
        build_name="build_centos_stream_rpm",
        build_status="failed",
        project_id=678,
    )

    project_content = {"name": "a project", "id": 678, "web_url": "an url"}
    failed_job_content = {
        "commit": {"author_email": "admin@example.com", "author_name": "Administrator"},
        "coverage": None,
        "allow_failure": False,
        "created_at": "2015-12-24T15:51:21.880Z",
        "started_at": "2015-12-24T17:54:30.733Z",
        "finished_at": "2015-12-24T17:54:31.198Z",
        "duration": 0.465,
        "queued_duration": 0.010,
        "artifacts_expire_at": "2016-01-23T17:54:31.198Z",
        "tag_list": ["docker runner", "macos-10.15"],
        "id": 1,
        "name": "rubocop",
        "pipeline": {"id": 456, "project_id": 678},
        "ref": "main",
        "artifacts": [],
        "runner": None,
        "stage": "test",
        "status": "failed",
        "tag": False,
        "web_url": "https://example.com/foo/bar/-/jobs/1",
        "user": {"id": 1},
    }
    pipeline_content = {
        "id": 456,
        "project_id": 678,
        "status": "pending",
        "ref": "refs/merge-requests/99/source",
        "before_sha": "a91957a858320c0e17f3a0eca7cfacbff50ea29a",
        "tag": False,
        "yaml_errors": None,
        "user": {
            "name": "Administrator",
            "username": "root",
            "id": 1,
            "state": "active",
            "avatar_url": ("http://www.gravatar.com/avatar/"
                           "e64c7d89f26bd1972efa854d13d7dd61?s=80&d=identicon"),
            "web_url": "http://localhost:3000/root",
        },
        "created_at": "2016-08-11T11:28:34.085Z",
        "updated_at": "2016-08-11T11:32:35.169Z",
        "started_at": None,
        "finished_at": "2016-08-11T11:32:35.145Z",
        "committed_at": None,
        "duration": None,
        "queued_duration": 0.010,
        "coverage": None,
        "web_url": "https://example.com/foo/bar/pipelines/46",
        "source": "merge_request_event",
    }

    mocked_headers = {
        "Content-Length": "12345",
        "Content-Type": "application/zip",
        "ETag": "abc123",
    }

    mocked_llama_response = """
{
  "choices": [
    {
      "text": "A clever response",
      "logprobs": []
    }
  ]
}
"""

    with responses.RequestsMock() as sync_rsps:
        with aioresponses.aioresponses() as async_rsps:
            async_rsps.head(
                url="https://gitlab.com/projects/678/jobs/1/artifacts",
                status=200,
                headers=mocked_headers,
            )
            async_rsps.post(
                url="http://llama-cpp-server:8000/v1/completions",
                body=mocked_llama_response,
            )
            sync_rsps.add(
                method=responses.GET,
                url="https://gitlab.com/api/v4/projects/678",
                json=project_content,
                content_type="application/json",
                status=200,
            )
            sync_rsps.add(
                method=responses.GET,
                url="https://gitlab.com/api/v4/projects/678/jobs/123",
                json=failed_job_content,
                content_type="application/json",
                status=200,
            )
            sync_rsps.add(
                method=responses.GET,
                url="https://gitlab.com/api/v4/projects/678/pipelines/456",
                json=pipeline_content,
                content_type="application/json",
                status=200,
            )
            sync_rsps.add(
                method=responses.GET,
                url="https://gitlab.com/api/v4/projects/678/jobs/1/artifacts",
                content_type="application/zip",
                body=create_zip_content("kojilogs/noarch-XXXXXX/x86_64-XXXXXX/"),
                status=200,
            )
            yield sync_rsps, async_rsps, job_hook


@pytest.mark.asyncio
async def test_process_gitlab_job_event(mock_config, mock_job_hook):
    _, _, job_hook = mock_job_hook
    await process_gitlab_job_event(http=aiohttp.ClientSession(), job_hook=job_hook)
