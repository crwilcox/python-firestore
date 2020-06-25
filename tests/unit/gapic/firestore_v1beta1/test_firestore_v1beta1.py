# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest

from google import auth
from google.api_core import client_options
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.firestore_v1beta1.services.firestore import FirestoreAsyncClient
from google.cloud.firestore_v1beta1.services.firestore import FirestoreClient
from google.cloud.firestore_v1beta1.services.firestore import pagers
from google.cloud.firestore_v1beta1.services.firestore import transports
from google.cloud.firestore_v1beta1.types import common
from google.cloud.firestore_v1beta1.types import document
from google.cloud.firestore_v1beta1.types import document as gf_document
from google.cloud.firestore_v1beta1.types import firestore
from google.cloud.firestore_v1beta1.types import query
from google.cloud.firestore_v1beta1.types import write
from google.cloud.firestore_v1beta1.types import write as gf_write
from google.oauth2 import service_account
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.protobuf import wrappers_pb2 as wrappers  # type: ignore
from google.type import latlng_pb2 as latlng  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert FirestoreClient._get_default_mtls_endpoint(None) is None
    assert FirestoreClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    assert (
        FirestoreClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        FirestoreClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        FirestoreClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert FirestoreClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi


@pytest.mark.parametrize("client_class", [FirestoreClient, FirestoreAsyncClient])
def test_firestore_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "firestore.googleapis.com:443"


def test_firestore_client_get_transport_class():
    transport = FirestoreClient.get_transport_class()
    assert transport == transports.FirestoreGrpcTransport

    transport = FirestoreClient.get_transport_class("grpc")
    assert transport == transports.FirestoreGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (FirestoreClient, transports.FirestoreGrpcTransport, "grpc"),
        (
            FirestoreAsyncClient,
            transports.FirestoreGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_firestore_client_client_options(client_class, transport_class, transport_name):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(FirestoreClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(FirestoreClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
            credentials=None,
            host="squid.clam.whelk",
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "never".
    os.environ["GOOGLE_API_USE_MTLS"] = "never"
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class()
        patched.assert_called_once_with(
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            credentials=None,
            host=client.DEFAULT_ENDPOINT,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "always".
    os.environ["GOOGLE_API_USE_MTLS"] = "always"
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class()
        patched.assert_called_once_with(
            api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
            client_cert_source=None,
            credentials=None,
            host=client.DEFAULT_MTLS_ENDPOINT,
        )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and client_cert_source is provided.
    os.environ["GOOGLE_API_USE_MTLS"] = "auto"
    options = client_options.ClientOptions(
        client_cert_source=client_cert_source_callback
    )
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
            client_cert_source=client_cert_source_callback,
            credentials=None,
            host=client.DEFAULT_MTLS_ENDPOINT,
        )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and default_client_cert_source is provided.
    os.environ["GOOGLE_API_USE_MTLS"] = "auto"
    with mock.patch.object(transport_class, "__init__") as patched:
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=True,
        ):
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                client_cert_source=None,
                credentials=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
            )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", but client_cert_source and default_client_cert_source are None.
    os.environ["GOOGLE_API_USE_MTLS"] = "auto"
    with mock.patch.object(transport_class, "__init__") as patched:
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=False,
        ):
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                api_mtls_endpoint=client.DEFAULT_ENDPOINT,
                client_cert_source=None,
                credentials=None,
                host=client.DEFAULT_ENDPOINT,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS has
    # unsupported value.
    os.environ["GOOGLE_API_USE_MTLS"] = "Unsupported"
    with pytest.raises(MutualTLSChannelError):
        client = client_class()

    del os.environ["GOOGLE_API_USE_MTLS"]


def test_firestore_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.firestore_v1beta1.services.firestore.transports.FirestoreGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = FirestoreClient(client_options={"api_endpoint": "squid.clam.whelk"})
        grpc_transport.assert_called_once_with(
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
            credentials=None,
            host="squid.clam.whelk",
        )


def test_get_document(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.GetDocumentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = document.Document(name="name_value",)

        response = client.get_document(request={"name": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, document.Document)
    assert response.name == "name_value"


@pytest.mark.asyncio
async def test_get_document_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.GetDocumentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_document), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            document.Document(name="name_value",)
        )

        response = await client.get_document(request={"name": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, document.Document)
    assert response.name == "name_value"


def test_get_document_field_headers():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.GetDocumentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_document), "__call__") as call:
        call.return_value = document.Document()

        client.get_document(request={"name": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_document_field_headers_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.GetDocumentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_document), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(document.Document())

        await client.get_document(request={"name": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_list_documents(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.ListDocumentsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_documents), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.ListDocumentsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_documents(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDocumentsPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_documents_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.ListDocumentsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_documents), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.ListDocumentsResponse(next_page_token="next_page_token_value",)
        )

        response = await client.list_documents(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDocumentsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_documents_field_headers():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.ListDocumentsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_documents), "__call__") as call:
        call.return_value = firestore.ListDocumentsResponse()

        client.list_documents(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_documents_field_headers_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.ListDocumentsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_documents), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.ListDocumentsResponse()
        )

        await client.list_documents(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_documents_pager():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_documents), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                    document.Document(),
                ],
                next_page_token="abc",
            ),
            firestore.ListDocumentsResponse(documents=[], next_page_token="def",),
            firestore.ListDocumentsResponse(
                documents=[document.Document(),], next_page_token="ghi",
            ),
            firestore.ListDocumentsResponse(
                documents=[document.Document(), document.Document(),],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_documents(request={},)]
        assert len(results) == 6
        assert all(isinstance(i, document.Document) for i in results)


def test_list_documents_pages():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_documents), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                    document.Document(),
                ],
                next_page_token="abc",
            ),
            firestore.ListDocumentsResponse(documents=[], next_page_token="def",),
            firestore.ListDocumentsResponse(
                documents=[document.Document(),], next_page_token="ghi",
            ),
            firestore.ListDocumentsResponse(
                documents=[document.Document(), document.Document(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_documents(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_documents_async_pager():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_documents),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                    document.Document(),
                ],
                next_page_token="abc",
            ),
            firestore.ListDocumentsResponse(documents=[], next_page_token="def",),
            firestore.ListDocumentsResponse(
                documents=[document.Document(),], next_page_token="ghi",
            ),
            firestore.ListDocumentsResponse(
                documents=[document.Document(), document.Document(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_documents(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, document.Document) for i in responses)


@pytest.mark.asyncio
async def test_list_documents_async_pages():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_documents),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                    document.Document(),
                ],
                next_page_token="abc",
            ),
            firestore.ListDocumentsResponse(documents=[], next_page_token="def",),
            firestore.ListDocumentsResponse(
                documents=[document.Document(),], next_page_token="ghi",
            ),
            firestore.ListDocumentsResponse(
                documents=[document.Document(), document.Document(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page in (await client.list_documents(request={})).pages:
            pages.append(page)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_create_document(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.CreateDocumentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = document.Document(name="name_value",)

        response = client.create_document(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, document.Document)
    assert response.name == "name_value"


@pytest.mark.asyncio
async def test_create_document_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.CreateDocumentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_document), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            document.Document(name="name_value",)
        )

        response = await client.create_document(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, document.Document)
    assert response.name == "name_value"


def test_create_document_field_headers():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.CreateDocumentRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_document), "__call__") as call:
        call.return_value = document.Document()

        client.create_document(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_document_field_headers_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.CreateDocumentRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_document), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(document.Document())

        await client.create_document(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_update_document(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.UpdateDocumentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gf_document.Document(name="name_value",)

        response = client.update_document(request={"document": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gf_document.Document)
    assert response.name == "name_value"


@pytest.mark.asyncio
async def test_update_document_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.UpdateDocumentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_document), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gf_document.Document(name="name_value",)
        )

        response = await client.update_document(request={"document": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gf_document.Document)
    assert response.name == "name_value"


def test_update_document_field_headers():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.UpdateDocumentRequest()
    request.document.name = "document.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_document), "__call__") as call:
        call.return_value = gf_document.Document()

        client.update_document(request={"document": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "document.name=document.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_document_field_headers_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.UpdateDocumentRequest()
    request.document.name = "document.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_document), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gf_document.Document()
        )

        await client.update_document(request={"document": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "document.name=document.name/value",) in kw[
        "metadata"
    ]


def test_update_document_flattened():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gf_document.Document()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_document(
            request={
                "document": gf_document.Document(name="name_value"),
                "update_mask": common.DocumentMask(field_paths=["field_paths_value"]),
            }
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].document == gf_document.Document(name="name_value")
        assert args[0].update_mask == common.DocumentMask(
            field_paths=["field_paths_value"]
        )


def test_update_document_flattened_error():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_document(
            request={
                "document": firestore.UpdateDocumentRequest(),
                "update_mask": gf_document.Document(name="name_value"),
                "mask": common.DocumentMask(field_paths=["field_paths_value"]),
            }
        )


@pytest.mark.asyncio
async def test_update_document_flattened_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_document), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gf_document.Document()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gf_document.Document()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_document(
            request={
                "document": gf_document.Document(name="name_value"),
                "update_mask": common.DocumentMask(field_paths=["field_paths_value"]),
            }
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].document == gf_document.Document(name="name_value")
        assert args[0].update_mask == common.DocumentMask(
            field_paths=["field_paths_value"]
        )


@pytest.mark.asyncio
async def test_update_document_flattened_error_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_document(
            request={
                "document": firestore.UpdateDocumentRequest(),
                "update_mask": gf_document.Document(name="name_value"),
                "mask": common.DocumentMask(field_paths=["field_paths_value"]),
            }
        )


def test_delete_document(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.DeleteDocumentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_document(request={"name": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_delete_document_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.DeleteDocumentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_document), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_document(request={"name": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_document_field_headers():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.DeleteDocumentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_document), "__call__") as call:
        call.return_value = None

        client.delete_document(request={"name": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_document_field_headers_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.DeleteDocumentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_document), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_document(request={"name": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_document_flattened():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_document(request={"name": "name_value"})

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_document_flattened_error():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_document(
            request={
                "name": firestore.DeleteDocumentRequest(),
                "current_document": "name_value",
            }
        )


@pytest.mark.asyncio
async def test_delete_document_flattened_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_document), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_document(request={"name": "name_value"})

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_document_flattened_error_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_document(
            request={
                "name": firestore.DeleteDocumentRequest(),
                "current_document": "name_value",
            }
        )


def test_batch_get_documents(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.BatchGetDocumentsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.batch_get_documents), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter([firestore.BatchGetDocumentsResponse()])

        response = client.batch_get_documents(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    for message in response:
        assert isinstance(message, firestore.BatchGetDocumentsResponse)


@pytest.mark.asyncio
async def test_batch_get_documents_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.BatchGetDocumentsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.batch_get_documents), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.BatchGetDocumentsResponse()]
        )

        response = await client.batch_get_documents(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    message = await response.read()
    assert isinstance(message, firestore.BatchGetDocumentsResponse)


def test_batch_get_documents_field_headers():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.BatchGetDocumentsRequest()
    request.database = "database/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.batch_get_documents), "__call__"
    ) as call:
        call.return_value = iter([firestore.BatchGetDocumentsResponse()])

        client.batch_get_documents(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "database=database/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_batch_get_documents_field_headers_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.BatchGetDocumentsRequest()
    request.database = "database/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.batch_get_documents), "__call__"
    ) as call:
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.BatchGetDocumentsResponse()]
        )

        await client.batch_get_documents(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "database=database/value",) in kw["metadata"]


def test_begin_transaction(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.BeginTransactionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.begin_transaction), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.BeginTransactionResponse(
            transaction=b"transaction_blob",
        )

        response = client.begin_transaction(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.BeginTransactionResponse)
    assert response.transaction == b"transaction_blob"


@pytest.mark.asyncio
async def test_begin_transaction_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.BeginTransactionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.begin_transaction), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.BeginTransactionResponse(transaction=b"transaction_blob",)
        )

        response = await client.begin_transaction(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.BeginTransactionResponse)
    assert response.transaction == b"transaction_blob"


def test_begin_transaction_field_headers():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.BeginTransactionRequest()
    request.database = "database/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.begin_transaction), "__call__"
    ) as call:
        call.return_value = firestore.BeginTransactionResponse()

        client.begin_transaction(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "database=database/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_begin_transaction_field_headers_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.BeginTransactionRequest()
    request.database = "database/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.begin_transaction), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.BeginTransactionResponse()
        )

        await client.begin_transaction(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "database=database/value",) in kw["metadata"]


def test_begin_transaction_flattened():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.begin_transaction), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.BeginTransactionResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.begin_transaction(request={"database": "database_value"})

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].database == "database_value"


def test_begin_transaction_flattened_error():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.begin_transaction(
            request={
                "database": firestore.BeginTransactionRequest(),
                "options": "database_value",
            }
        )


@pytest.mark.asyncio
async def test_begin_transaction_flattened_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.begin_transaction), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.BeginTransactionResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.BeginTransactionResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.begin_transaction(
            request={"database": "database_value"}
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].database == "database_value"


@pytest.mark.asyncio
async def test_begin_transaction_flattened_error_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.begin_transaction(
            request={
                "database": firestore.BeginTransactionRequest(),
                "options": "database_value",
            }
        )


def test_commit(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.CommitRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.commit), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.CommitResponse()

        response = client.commit(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.CommitResponse)


@pytest.mark.asyncio
async def test_commit_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.CommitRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._client._transport.commit), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.CommitResponse()
        )

        response = await client.commit(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.CommitResponse)


def test_commit_field_headers():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.CommitRequest()
    request.database = "database/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.commit), "__call__") as call:
        call.return_value = firestore.CommitResponse()

        client.commit(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "database=database/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_commit_field_headers_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.CommitRequest()
    request.database = "database/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._client._transport.commit), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.CommitResponse()
        )

        await client.commit(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "database=database/value",) in kw["metadata"]


def test_commit_flattened():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.commit), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.CommitResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.commit(
            request={
                "database": "database_value",
                "writes": [
                    gf_write.Write(update=gf_document.Document(name="name_value"))
                ],
            }
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].database == "database_value"
        assert args[0].writes == [
            gf_write.Write(update=gf_document.Document(name="name_value"))
        ]


def test_commit_flattened_error():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.commit(
            request={
                "database": firestore.CommitRequest(),
                "writes": "database_value",
                "transaction": [
                    gf_write.Write(update=gf_document.Document(name="name_value"))
                ],
            }
        )


@pytest.mark.asyncio
async def test_commit_flattened_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._client._transport.commit), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.CommitResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.CommitResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.commit(
            request={
                "database": "database_value",
                "writes": [
                    gf_write.Write(update=gf_document.Document(name="name_value"))
                ],
            }
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].database == "database_value"
        assert args[0].writes == [
            gf_write.Write(update=gf_document.Document(name="name_value"))
        ]


@pytest.mark.asyncio
async def test_commit_flattened_error_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.commit(
            request={
                "database": firestore.CommitRequest(),
                "writes": "database_value",
                "transaction": [
                    gf_write.Write(update=gf_document.Document(name="name_value"))
                ],
            }
        )


def test_rollback(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.RollbackRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.rollback), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.rollback(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_rollback_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.RollbackRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.rollback), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.rollback(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_rollback_field_headers():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.RollbackRequest()
    request.database = "database/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.rollback), "__call__") as call:
        call.return_value = None

        client.rollback(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "database=database/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_rollback_field_headers_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.RollbackRequest()
    request.database = "database/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.rollback), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.rollback(request={"database": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "database=database/value",) in kw["metadata"]


def test_rollback_flattened():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.rollback), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.rollback(
            request={"database": "database_value", "transaction": b"transaction_blob"}
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].database == "database_value"
        assert args[0].transaction == b"transaction_blob"


def test_rollback_flattened_error():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.rollback(
            request={
                "database": firestore.RollbackRequest(),
                "transaction": "database_value",
            }
        )


@pytest.mark.asyncio
async def test_rollback_flattened_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.rollback), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.rollback(
            request={"database": "database_value", "transaction": b"transaction_blob"}
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].database == "database_value"
        assert args[0].transaction == b"transaction_blob"


@pytest.mark.asyncio
async def test_rollback_flattened_error_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.rollback(
            request={
                "database": firestore.RollbackRequest(),
                "transaction": "database_value",
            }
        )


def test_run_query(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.RunQueryRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.run_query), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter([firestore.RunQueryResponse()])

        response = client.run_query(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    for message in response:
        assert isinstance(message, firestore.RunQueryResponse)


@pytest.mark.asyncio
async def test_run_query_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.RunQueryRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.run_query), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.RunQueryResponse()]
        )

        response = await client.run_query(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    message = await response.read()
    assert isinstance(message, firestore.RunQueryResponse)


def test_run_query_field_headers():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.RunQueryRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.run_query), "__call__") as call:
        call.return_value = iter([firestore.RunQueryResponse()])

        client.run_query(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_run_query_field_headers_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.RunQueryRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.run_query), "__call__"
    ) as call:
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.RunQueryResponse()]
        )

        await client.run_query(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_write(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.WriteRequest()

    requests = [request]

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.write), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter([firestore.WriteResponse()])

        response = client.write(request={"database": iter(requests)})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert next(args[0]) == request

    # Establish that the response is the type that we expect.
    for message in response:
        assert isinstance(message, firestore.WriteResponse)


@pytest.mark.asyncio
async def test_write_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.WriteRequest()

    requests = [request]

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._client._transport.write), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = mock.Mock(aio.StreamStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(side_effect=[firestore.WriteResponse()])

        response = await client.write(request={"database": iter(requests)})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert next(args[0]) == request

    # Establish that the response is the type that we expect.
    message = await response.read()
    assert isinstance(message, firestore.WriteResponse)


def test_listen(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.ListenRequest()

    requests = [request]

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.listen), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter([firestore.ListenResponse()])

        response = client.listen(request={"database": iter(requests)})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert next(args[0]) == request

    # Establish that the response is the type that we expect.
    for message in response:
        assert isinstance(message, firestore.ListenResponse)


@pytest.mark.asyncio
async def test_listen_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.ListenRequest()

    requests = [request]

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._client._transport.listen), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = mock.Mock(aio.StreamStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.ListenResponse()]
        )

        response = await client.listen(request={"database": iter(requests)})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert next(args[0]) == request

    # Establish that the response is the type that we expect.
    message = await response.read()
    assert isinstance(message, firestore.ListenResponse)


def test_list_collection_ids(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.ListCollectionIdsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_collection_ids), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.ListCollectionIdsResponse(
            collection_ids=["collection_ids_value"],
            next_page_token="next_page_token_value",
        )

        response = client.list_collection_ids(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.ListCollectionIdsResponse)
    assert response.collection_ids == ["collection_ids_value"]
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_collection_ids_async(transport: str = "grpc_asyncio"):
    client = FirestoreAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = firestore.ListCollectionIdsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_collection_ids), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.ListCollectionIdsResponse(
                collection_ids=["collection_ids_value"],
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_collection_ids(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.ListCollectionIdsResponse)
    assert response.collection_ids == ["collection_ids_value"]
    assert response.next_page_token == "next_page_token_value"


def test_list_collection_ids_field_headers():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.ListCollectionIdsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_collection_ids), "__call__"
    ) as call:
        call.return_value = firestore.ListCollectionIdsResponse()

        client.list_collection_ids(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_collection_ids_field_headers_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.ListCollectionIdsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_collection_ids), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.ListCollectionIdsResponse()
        )

        await client.list_collection_ids(request={"parent": request})

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_collection_ids_flattened():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_collection_ids), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.ListCollectionIdsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_collection_ids(request={"parent": "parent_value"})

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_collection_ids_flattened_error():
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_collection_ids(
            request={
                "parent": firestore.ListCollectionIdsRequest(),
                "page_size": "parent_value",
            }
        )


@pytest.mark.asyncio
async def test_list_collection_ids_flattened_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_collection_ids), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.ListCollectionIdsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.ListCollectionIdsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_collection_ids(request={"parent": "parent_value"})

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_collection_ids_flattened_error_async():
    client = FirestoreAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_collection_ids(
            request={
                "parent": firestore.ListCollectionIdsRequest(),
                "page_size": "parent_value",
            }
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.FirestoreGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = FirestoreClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.FirestoreGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = FirestoreClient(transport=transport)
    assert client._transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.FirestoreGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.FirestoreGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = FirestoreClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.FirestoreGrpcTransport,)


def test_firestore_base_transport():
    # Instantiate the base transport.
    transport = transports.FirestoreTransport(
        credentials=credentials.AnonymousCredentials(),
    )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "get_document",
        "list_documents",
        "create_document",
        "update_document",
        "delete_document",
        "batch_get_documents",
        "begin_transaction",
        "commit",
        "rollback",
        "run_query",
        "write",
        "listen",
        "list_collection_ids",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())


def test_firestore_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        FirestoreClient()
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/datastore",
            )
        )


def test_firestore_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.FirestoreGrpcTransport(host="squid.clam.whelk")
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/datastore",
            )
        )


def test_firestore_host_no_port():
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="firestore.googleapis.com"
        ),
    )
    assert client._transport._host == "firestore.googleapis.com:443"


def test_firestore_host_with_port():
    client = FirestoreClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="firestore.googleapis.com:8000"
        ),
    )
    assert client._transport._host == "firestore.googleapis.com:8000"


def test_firestore_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.FirestoreGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


def test_firestore_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.FirestoreGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_firestore_grpc_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.FirestoreGrpcTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        ssl_credentials=mock_ssl_cred,
        scopes=(
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/datastore",
        ),
    )
    assert transport.grpc_channel == mock_grpc_channel


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_firestore_grpc_asyncio_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.FirestoreGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        ssl_credentials=mock_ssl_cred,
        scopes=(
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/datastore",
        ),
    )
    assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_firestore_grpc_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.FirestoreGrpcTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            ssl_credentials=mock_ssl_cred,
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/datastore",
            ),
        )
        assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_firestore_grpc_asyncio_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.FirestoreGrpcAsyncIOTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            ssl_credentials=mock_ssl_cred,
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/datastore",
            ),
        )
        assert transport.grpc_channel == mock_grpc_channel
