{
  description = "Chatbot AI dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";

      pkgs = import nixpkgs {
				inherit system;

				config = {
					allowUnfree = true;
				};
			};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          pkg-config
          meson
          ninja
          libGL
          mesa
          gtk4
          glib
          graphene
          gdk-pixbuf
          cairo
          pango
          harfbuzz
          libadwaita
          python313Packages.pygobject3
          wrapGAppsHook4
          cudaPackages.cudatoolkit
          cudaPackages.cudnn
        ];

        shellHook = ''
          export SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt
          export XLA_FLAGS=--xla_gpu_cuda_data_dir=${pkgs.cudaPackages.cudatoolkit}

          export LD_LIBRARY_PATH=/run/opengl-driver/lib:${
						pkgs.lib.makeLibraryPath [
							pkgs.libGL
							pkgs.mesa
							pkgs.gtk4
							pkgs.glib
							pkgs.graphene
							pkgs.gdk-pixbuf
							pkgs.cairo
							pkgs.pango
							pkgs.harfbuzz
							pkgs.libadwaita
							pkgs.cudaPackages.cudatoolkit
							pkgs.cudaPackages.cudnn
						]
					}:$LD_LIBRARY_PATH

          export GI_TYPELIB_PATH="${pkgs.gtk4}/lib/girepository-1.0:${pkgs.glib}/lib/girepository-1.0:${pkgs.graphene}/lib/girepository-1.0:${pkgs.gdk-pixbuf}/lib/girepository-1.0:${pkgs.cairo}/lib/girepository-1.0:${pkgs.pango}/lib/girepository-1.0:${pkgs.harfbuzz}/lib/girepository-1.0:${pkgs.libadwaita}/lib/girepository-1.0:$GI_TYPELIB_PATH"

          echo "🐍 Chatbot AI environment loaded (GTK4)"
        '';
      };
    };
}
