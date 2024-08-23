{
  description = "Flake for kube-dump-to-s3";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    kube-dump = {
      url = "github:WoozyMasta/kube-dump?ref=1.1.2";
      flake = false;
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }@inputs:

    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        python = pkgs.python3.withPackages (ps: pythonPkgs);
        pythonPkgs = with pkgs.python3.pkgs; [
          setuptools
          pydantic
          pydantic-settings
          coloredlogs
          boto3
          boto3-stubs
          mypy-boto3-s3
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          packages =
            with pkgs;
            with self.packages.${system};
            [
              just
              nixfmt-rfc-style

              pyright
              python
              python.pkgs.black

              podman
              docker
              kube-dump
            ];
        };

        packages = rec {
          default = kube-dump-to-s3;

          kube-dump-to-s3 =
            with python.pkgs;
            buildPythonApplication rec {
              name = "kube-dump-to-s3";
              src = ./.;
              format = "pyproject";

              propagatedBuildInputs = pythonPkgs;

              runtimeDeps =
                with pkgs;
                with self.packages.${system};
                [
                  kube-dump
                  zstd
                ];

              preFixup = ''
                makeWrapperArgs+=( --prefix PATH : ${lib.makeBinPath runtimeDeps} )
              '';

              meta.mainProgram = "kube-dump-to-s3";
            };

          kube-dump = pkgs.writeShellApplication {
            name = "kube-dump";
            text = builtins.readFile "${inputs.kube-dump}/kube-dump";
            runtimeInputs = with pkgs; [
              kubectl
              curl
              jq
              yq-go
              xz
              gzip
              bzip2
              gnutar
            ];

            # kube-dump comes with its own bash options.
            bashOptions = [ ];

            # Make writeShellApplication's shellcheck less strict since this is
            # not even our code.
            derivationArgs.SHELLCHECK_OPTS = "--severity=error";
          };
        };
      }
    );
}
