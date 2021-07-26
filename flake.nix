{
  inputs.nixos-cn.url = "github:nixos-cn/flakes";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixos-cn, nixpkgs, flake-utils }:
    with flake-utils.lib;
    eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        extra = nixos-cn.legacyPackages.${system};
      in with pkgs; {
        devShell = mkShell {
          packages = [
            (python3.withPackages
              (p: [ extra.python-packages.yubiotp p.flask ]))
          ];
        };
      });
}
