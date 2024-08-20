{
  imageName,
  imageTag,
  system ? "x86_64-linux",
}:

let
  self = builtins.getFlake (toString ./.);

  pkgs = self.inputs.nixpkgs.legacyPackages.${system};
  lib = pkgs.lib;
in

pkgs.dockerTools.buildImage {
  name = imageName;
  tag = imageTag;
  config.Entrypoint = [ "${lib.getExe self.packages.${system}.kube-dump-to-s3}" ];
}
