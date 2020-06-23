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

from typing import Awaitable, Callable, Dict, Optional, Sequence, Tuple

from google.api_core import grpc_helpers_async  # type: ignore
from google.auth import credentials  # type: ignore
from google.auth.transport.grpc import SslCredentials  # type: ignore

import grpc  # type: ignore
from grpc.experimental import aio  # type: ignore

from google.cloud.firestore_v1.types import document
from google.cloud.firestore_v1.types import document as gf_document
from google.cloud.firestore_v1.types import firestore
from google.protobuf import empty_pb2 as empty  # type: ignore

from .base import FirestoreTransport
from .grpc import FirestoreGrpcTransport


class FirestoreGrpcAsyncIOTransport(FirestoreTransport):
    """gRPC AsyncIO backend transport for Firestore.

    The Cloud Firestore service.
    Cloud Firestore is a fast, fully managed, serverless, cloud-
    native NoSQL document database that simplifies storing, syncing,
    and querying data for your mobile, web, and IoT apps at global
    scale. Its client libraries provide live synchronization and
    offline support, while its security features and integrations
    with Firebase and Google Cloud Platform (GCP) accelerate
    building truly serverless apps.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends protocol buffers over the wire using gRPC (which is built on
    top of HTTP/2); the ``grpcio`` package must be installed.
    """

    _grpc_channel: aio.Channel
    _stubs: Dict[str, Callable] = {}

    @classmethod
    def create_channel(
        cls,
        host: str = "firestore.googleapis.com",
        credentials: credentials.Credentials = None,
        scopes: Optional[Sequence[str]] = None,
        **kwargs
    ) -> aio.Channel:
        """Create and return a gRPC AsyncIO channel object.
        Args:
            address (Optional[str]): The host for the channel to use.
            credentials (Optional[~.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify this application to the service. If
                none are specified, the client will attempt to ascertain
                the credentials from the environment.
            scopes (Optional[Sequence[str]]): A optional list of scopes needed for this
                service. These are only used when credentials are not specified and
                are passed to :func:`google.auth.default`.
            kwargs (Optional[dict]): Keyword arguments, which are passed to the
                channel creation.
        Returns:
            aio.Channel: A gRPC AsyncIO channel object.
        """
        scopes = scopes or cls.AUTH_SCOPES
        return grpc_helpers_async.create_channel(
            host, credentials=credentials, scopes=scopes, **kwargs
        )

    def __init__(
        self,
        *,
        host: str = "firestore.googleapis.com",
        credentials: credentials.Credentials = None,
        channel: aio.Channel = None,
        api_mtls_endpoint: str = None,
        client_cert_source: Callable[[], Tuple[bytes, bytes]] = None
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]): The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
                This argument is ignored if ``channel`` is provided.
            channel (Optional[aio.Channel]): A ``Channel`` instance through
                which to make calls.
            api_mtls_endpoint (Optional[str]): The mutual TLS endpoint. If
                provided, it overrides the ``host`` argument and tries to create
                a mutual TLS channel with client SSL credentials from
                ``client_cert_source`` or applicatin default SSL credentials.
            client_cert_source (Optional[Callable[[], Tuple[bytes, bytes]]]): A
                callback to provide client SSL certificate bytes and private key
                bytes, both in PEM format. It is ignored if ``api_mtls_endpoint``
                is None.

        Raises:
          google.auth.exceptions.MutualTlsChannelError: If mutual TLS transport
              creation failed for any reason.
        """
        if channel:
            # Sanity check: Ensure that channel and credentials are not both
            # provided.
            credentials = False

            # If a channel was explicitly provided, set it.
            self._grpc_channel = channel
        elif api_mtls_endpoint:
            host = (
                api_mtls_endpoint
                if ":" in api_mtls_endpoint
                else api_mtls_endpoint + ":443"
            )

            # Create SSL credentials with client_cert_source or application
            # default SSL credentials.
            if client_cert_source:
                cert, key = client_cert_source()
                ssl_credentials = grpc.ssl_channel_credentials(
                    certificate_chain=cert, private_key=key
                )
            else:
                ssl_credentials = SslCredentials().ssl_credentials

            # create a new channel. The provided one is ignored.
            self._grpc_channel = type(self).create_channel(
                host,
                credentials=credentials,
                ssl_credentials=ssl_credentials,
                scopes=self.AUTH_SCOPES,
            )

        # Run the base constructor.
        super().__init__(host=host, credentials=credentials)
        self._stubs = {}

    @property
    def grpc_channel(self) -> aio.Channel:
        """Create the channel designed to connect to this service.

        This property caches on the instance; repeated calls return
        the same channel.
        """
        # Sanity check: Only create a new channel if we do not already
        # have one.
        if not hasattr(self, "_grpc_channel"):
            self._grpc_channel = self.create_channel(
                self._host, credentials=self._credentials,
            )

        # Return the channel from cache.
        return self._grpc_channel

    @property
    def get_document(
        self,
    ) -> Callable[[firestore.GetDocumentRequest], Awaitable[document.Document]]:
        r"""Return a callable for the get document method over gRPC.

        Gets a single document.

        Returns:
            Callable[[~.GetDocumentRequest],
                    Awaitable[~.Document]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_document" not in self._stubs:
            self._stubs["get_document"] = self.grpc_channel.unary_unary(
                "/google.cloud.firestore.v1.Firestore/GetDocument",
                request_serializer=firestore.GetDocumentRequest.serialize,
                response_deserializer=document.Document.deserialize,
            )
        return self._stubs["get_document"]

    @property
    def list_documents(
        self,
    ) -> Callable[
        [firestore.ListDocumentsRequest], Awaitable[firestore.ListDocumentsResponse]
    ]:
        r"""Return a callable for the list documents method over gRPC.

        Lists documents.

        Returns:
            Callable[[~.ListDocumentsRequest],
                    Awaitable[~.ListDocumentsResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_documents" not in self._stubs:
            self._stubs["list_documents"] = self.grpc_channel.unary_unary(
                "/google.cloud.firestore.v1.Firestore/ListDocuments",
                request_serializer=firestore.ListDocumentsRequest.serialize,
                response_deserializer=firestore.ListDocumentsResponse.deserialize,
            )
        return self._stubs["list_documents"]

    @property
    def update_document(
        self,
    ) -> Callable[[firestore.UpdateDocumentRequest], Awaitable[gf_document.Document]]:
        r"""Return a callable for the update document method over gRPC.

        Updates or inserts a document.

        Returns:
            Callable[[~.UpdateDocumentRequest],
                    Awaitable[~.Document]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "update_document" not in self._stubs:
            self._stubs["update_document"] = self.grpc_channel.unary_unary(
                "/google.cloud.firestore.v1.Firestore/UpdateDocument",
                request_serializer=firestore.UpdateDocumentRequest.serialize,
                response_deserializer=gf_document.Document.deserialize,
            )
        return self._stubs["update_document"]

    @property
    def delete_document(
        self,
    ) -> Callable[[firestore.DeleteDocumentRequest], Awaitable[empty.Empty]]:
        r"""Return a callable for the delete document method over gRPC.

        Deletes a document.

        Returns:
            Callable[[~.DeleteDocumentRequest],
                    Awaitable[~.Empty]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_document" not in self._stubs:
            self._stubs["delete_document"] = self.grpc_channel.unary_unary(
                "/google.cloud.firestore.v1.Firestore/DeleteDocument",
                request_serializer=firestore.DeleteDocumentRequest.serialize,
                response_deserializer=empty.Empty.FromString,
            )
        return self._stubs["delete_document"]

    @property
    def batch_get_documents(
        self,
    ) -> Callable[
        [firestore.BatchGetDocumentsRequest],
        Awaitable[firestore.BatchGetDocumentsResponse],
    ]:
        r"""Return a callable for the batch get documents method over gRPC.

        Gets multiple documents.
        Documents returned by this method are not guaranteed to
        be returned in the same order that they were requested.

        Returns:
            Callable[[~.BatchGetDocumentsRequest],
                    Awaitable[~.BatchGetDocumentsResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "batch_get_documents" not in self._stubs:
            self._stubs["batch_get_documents"] = self.grpc_channel.unary_stream(
                "/google.cloud.firestore.v1.Firestore/BatchGetDocuments",
                request_serializer=firestore.BatchGetDocumentsRequest.serialize,
                response_deserializer=firestore.BatchGetDocumentsResponse.deserialize,
            )
        return self._stubs["batch_get_documents"]

    @property
    def begin_transaction(
        self,
    ) -> Callable[
        [firestore.BeginTransactionRequest],
        Awaitable[firestore.BeginTransactionResponse],
    ]:
        r"""Return a callable for the begin transaction method over gRPC.

        Starts a new transaction.

        Returns:
            Callable[[~.BeginTransactionRequest],
                    Awaitable[~.BeginTransactionResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "begin_transaction" not in self._stubs:
            self._stubs["begin_transaction"] = self.grpc_channel.unary_unary(
                "/google.cloud.firestore.v1.Firestore/BeginTransaction",
                request_serializer=firestore.BeginTransactionRequest.serialize,
                response_deserializer=firestore.BeginTransactionResponse.deserialize,
            )
        return self._stubs["begin_transaction"]

    @property
    def commit(
        self,
    ) -> Callable[[firestore.CommitRequest], Awaitable[firestore.CommitResponse]]:
        r"""Return a callable for the commit method over gRPC.

        Commits a transaction, while optionally updating
        documents.

        Returns:
            Callable[[~.CommitRequest],
                    Awaitable[~.CommitResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "commit" not in self._stubs:
            self._stubs["commit"] = self.grpc_channel.unary_unary(
                "/google.cloud.firestore.v1.Firestore/Commit",
                request_serializer=firestore.CommitRequest.serialize,
                response_deserializer=firestore.CommitResponse.deserialize,
            )
        return self._stubs["commit"]

    @property
    def rollback(self) -> Callable[[firestore.RollbackRequest], Awaitable[empty.Empty]]:
        r"""Return a callable for the rollback method over gRPC.

        Rolls back a transaction.

        Returns:
            Callable[[~.RollbackRequest],
                    Awaitable[~.Empty]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "rollback" not in self._stubs:
            self._stubs["rollback"] = self.grpc_channel.unary_unary(
                "/google.cloud.firestore.v1.Firestore/Rollback",
                request_serializer=firestore.RollbackRequest.serialize,
                response_deserializer=empty.Empty.FromString,
            )
        return self._stubs["rollback"]

    @property
    def run_query(
        self,
    ) -> Callable[[firestore.RunQueryRequest], Awaitable[firestore.RunQueryResponse]]:
        r"""Return a callable for the run query method over gRPC.

        Runs a query.

        Returns:
            Callable[[~.RunQueryRequest],
                    Awaitable[~.RunQueryResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "run_query" not in self._stubs:
            self._stubs["run_query"] = self.grpc_channel.unary_stream(
                "/google.cloud.firestore.v1.Firestore/RunQuery",
                request_serializer=firestore.RunQueryRequest.serialize,
                response_deserializer=firestore.RunQueryResponse.deserialize,
            )
        return self._stubs["run_query"]

    @property
    def partition_query(
        self,
    ) -> Callable[
        [firestore.PartitionQueryRequest], Awaitable[firestore.PartitionQueryResponse]
    ]:
        r"""Return a callable for the partition query method over gRPC.

        Partitions a query by returning partition cursors
        that can be used to run the query in parallel. The
        returned partition cursors are split points that can be
        used by RunQuery as starting/end points for the query
        results.

        Returns:
            Callable[[~.PartitionQueryRequest],
                    Awaitable[~.PartitionQueryResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "partition_query" not in self._stubs:
            self._stubs["partition_query"] = self.grpc_channel.unary_unary(
                "/google.cloud.firestore.v1.Firestore/PartitionQuery",
                request_serializer=firestore.PartitionQueryRequest.serialize,
                response_deserializer=firestore.PartitionQueryResponse.deserialize,
            )
        return self._stubs["partition_query"]

    @property
    def write(
        self,
    ) -> Callable[[firestore.WriteRequest], Awaitable[firestore.WriteResponse]]:
        r"""Return a callable for the write method over gRPC.

        Streams batches of document updates and deletes, in
        order.

        Returns:
            Callable[[~.WriteRequest],
                    Awaitable[~.WriteResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "write" not in self._stubs:
            self._stubs["write"] = self.grpc_channel.stream_stream(
                "/google.cloud.firestore.v1.Firestore/Write",
                request_serializer=firestore.WriteRequest.serialize,
                response_deserializer=firestore.WriteResponse.deserialize,
            )
        return self._stubs["write"]

    @property
    def listen(
        self,
    ) -> Callable[[firestore.ListenRequest], Awaitable[firestore.ListenResponse]]:
        r"""Return a callable for the listen method over gRPC.

        Listens to changes.

        Returns:
            Callable[[~.ListenRequest],
                    Awaitable[~.ListenResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "listen" not in self._stubs:
            self._stubs["listen"] = self.grpc_channel.stream_stream(
                "/google.cloud.firestore.v1.Firestore/Listen",
                request_serializer=firestore.ListenRequest.serialize,
                response_deserializer=firestore.ListenResponse.deserialize,
            )
        return self._stubs["listen"]

    @property
    def list_collection_ids(
        self,
    ) -> Callable[
        [firestore.ListCollectionIdsRequest],
        Awaitable[firestore.ListCollectionIdsResponse],
    ]:
        r"""Return a callable for the list collection ids method over gRPC.

        Lists all the collection IDs underneath a document.

        Returns:
            Callable[[~.ListCollectionIdsRequest],
                    Awaitable[~.ListCollectionIdsResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_collection_ids" not in self._stubs:
            self._stubs["list_collection_ids"] = self.grpc_channel.unary_unary(
                "/google.cloud.firestore.v1.Firestore/ListCollectionIds",
                request_serializer=firestore.ListCollectionIdsRequest.serialize,
                response_deserializer=firestore.ListCollectionIdsResponse.deserialize,
            )
        return self._stubs["list_collection_ids"]

    @property
    def batch_write(
        self,
    ) -> Callable[
        [firestore.BatchWriteRequest], Awaitable[firestore.BatchWriteResponse]
    ]:
        r"""Return a callable for the batch write method over gRPC.

        Applies a batch of write operations.

        The BatchWrite method does not apply the write operations
        atomically and can apply them out of order. Method does not
        allow more than one write per document. Each write succeeds or
        fails independently. See the
        [BatchWriteResponse][google.cloud.firestore.v1.BatchWriteResponse] for
        the success status of each write.

        If you require an atomically applied set of writes, use
        [Commit][google.cloud.firestore.v1.Firestore.Commit] instead.

        Returns:
            Callable[[~.BatchWriteRequest],
                    Awaitable[~.BatchWriteResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "batch_write" not in self._stubs:
            self._stubs["batch_write"] = self.grpc_channel.unary_unary(
                "/google.cloud.firestore.v1.Firestore/BatchWrite",
                request_serializer=firestore.BatchWriteRequest.serialize,
                response_deserializer=firestore.BatchWriteResponse.deserialize,
            )
        return self._stubs["batch_write"]

    @property
    def create_document(
        self,
    ) -> Callable[[firestore.CreateDocumentRequest], Awaitable[document.Document]]:
        r"""Return a callable for the create document method over gRPC.

        Creates a new document.

        Returns:
            Callable[[~.CreateDocumentRequest],
                    Awaitable[~.Document]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_document" not in self._stubs:
            self._stubs["create_document"] = self.grpc_channel.unary_unary(
                "/google.cloud.firestore.v1.Firestore/CreateDocument",
                request_serializer=firestore.CreateDocumentRequest.serialize,
                response_deserializer=document.Document.deserialize,
            )
        return self._stubs["create_document"]


__all__ = ("FirestoreGrpcAsyncIOTransport",)
