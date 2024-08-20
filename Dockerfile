FROM nixos/nix:2.24.3 AS builder

COPY . /build
WORKDIR /build

RUN nix --extra-experimental-features "nix-command flakes" build

RUN mkdir /nix-store-closure
RUN cp -R $(nix-store -qR /build/result/) /nix-store-closure


FROM scratch

COPY --from=builder /nix-store-closure /nix/store
COPY --from=builder /build/result /result

ENTRYPOINT ["/result/bin/kube-dump-to-s3"]
