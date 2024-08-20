FROM nixos/nix:latest AS builder

COPY . /build
WORKDIR /build

RUN nix --extra-experimental-features "nix-command flakes" build

RUN mkdir /nix-store-closure
RUN cp -R $(nix-store -qR result/) /nix-store-closure


FROM scratch

COPY --from=builder /nix-store-closure /nix/store
COPY --from=builder /build/result /result

RUN ln -s /result/bin/kube-dump-to-s3 /kube-dump-to-s3
ENTRYPOINT ["/kube-dump-to-s3"]
