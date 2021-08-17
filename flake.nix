{
  inputs.nixos-cn.url = "github:nixos-cn/flakes";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixos-cn, nixpkgs, flake-utils }:
    with flake-utils.lib;
    with nixpkgs.lib;
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

        packages.client = let
          out = placeholder "out";
          yubiotp = nixos-cn.legacyPackages.${system}.python-packages.yubiotp;
          python' = yubiotp.pythonModule;
          paths = concatMapStringsSep "," (m: "'${m}/${python'.sitePackages}'")
            (remove python' (yubiotp.requiredPythonModules ++ [ yubiotp ]));
        in runCommand "client" { } ''
          dest=${out}/lib/security/remote-otp
          mkdir -p $dest
          cp ${./client}/* $dest
          cd $dest
          cat <<EOF | cat - pam.py > temp
          import site
          import functools
          import pathlib
          current_package = pathlib.Path(__file__).parent.resolve()
          functools.reduce(lambda k, p: site.addsitedir(p, k), [current_package,${paths}], site._init_pathinfo())
          EOF
          mv temp pam.py
        '';
      });
}
