# STDS Projekt: BA-Chain

![Preview](presentation/demo.png)

## Demo
This code is live at [https://bac.tfld.de](https://bac.tfld.de).

## Structure
- presentation: contains presentation files for this project
- src: contains source code
	- core: main Django app for coordination of calculation and storing the results
	- manage.py: script to control the app, e.g. runserver, migrate, ...
	- projectControl: global settings for the Django project
	- rust_wasm: Rust source code for calculating hashes and communicating with backend
	- static: static files like pictures, stylesheets and scripts
	- templates: global templates

## Get started with Python/Django
1. Install `python python-virtualenv python-pip redis` (package names come from Arch Linux; Python 3.9 required).
2. Setup Redis to run on `localhost:6379`
3. Create and activate a python virtual environment.
4. Run `pip install -r requirements.txt` to install dependencies.
5. Edit `src/projectControl/settings.py` to change settings like database or security. No changes needed if you are developing.
6. Run `python src/manage.py migrate` to setup database scheme.
8. Run `python src/manage.py runserver` to start the django server (only for development!).

## Get started with Rust/WebAssembly
1. Install `rust rust-wasm wasm-pack redis` (package names come from Arch Linux).
2. Make changes to code in `src/rust_wasm` and compile it to WASM with `wasm-pack build --target web`.
3. Move the produced `src/rust_wasm/pkg` directory to `/src/static` with `cp -r src/rust_wasm/pkg src/static/`.

## Note
The app was developed using the web browsers Chrome/Chromium and Firefox, so the app may not work or look odd in other/older web browsers. We also did not take account of mobile users.

## License & copyright
© Martin Junghans & Max Hohlfeld  
The code in this repository is licensed under the [GNU AGPL v3](https://www.gnu.org/licenses/agpl-3.0.html) license.
