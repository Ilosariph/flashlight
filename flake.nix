{
  description = "DIY 14500 EDC flashlight: firmware, PCB, mechanical CAD";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems
        (system: f nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forAllSystems (pkgs:
        let
          avr = pkgs.pkgsCross.avr.buildPackages;
          # CadQuery isn't in nixpkgs: PyPI wheels (cadquery-ocp) in .venv,
          # these libs make the manylinux .so files load on NixOS.
          cqLibs = with pkgs; [
            stdenv.cc.cc.lib zlib expat libGL libglvnd fontconfig freetype
            libx11 libxext libxrender libxi libxcursor
          ];
        in
        {
          default = pkgs.mkShell {
            packages = [
              # firmware
              avr.gcc avr.binutils  # gcc wrapper bundles avr-libc
              pkgs.avrdude pkgs.python3Packages.pymcuprog pkgs.gnumake
              # CAD (kicad + openscad come from the system profile)
              pkgs.python312 pkgs.uv
            ];
            # cc-wrapper doesn't put avr-libc's avrxmega3 dir on the link path
            # (ATtiny 0/1/2-series): firmware/Makefile adds it from here.
            AVR_LIBC = "${avr.gcc.libc}/avr";
            LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath cqLibs;
            UV_PYTHON = "${pkgs.python312}/bin/python3";
            UV_PYTHON_DOWNLOADS = "never";
            shellHook = ''
              if [ ! -x .venv/bin/python ]; then
                uv venv -q .venv && uv pip install -q --python .venv/bin/python -r mech/requirements.txt
              fi
              export PATH="$PWD/.venv/bin:$PATH"
            '';
          };
        });
    };
}
