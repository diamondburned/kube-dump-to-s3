{
  imageName,
  imageTag,
  created ? null,
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
  inherit created;

  copyToRoot = pkgs.buildEnv {
    name = "kube-dump-to-s3-docker-env";
    paths = [ pkgs.bash ] ++ (builtins.attrValues self.packages.${system});
  };

  config.Entrypoint = [ "/bin/kube-dump-to-s3" ];
}
