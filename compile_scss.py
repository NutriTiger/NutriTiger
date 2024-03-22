import sass

def compile_scss(input_file, output_file):
    with open(input_file, 'r') as scss_file:
        scss_content = scss_file.read()
    css_content = sass.compile(string=scss_content)
    with open(output_file, 'w') as css_file:
        css_file.write(css_content)

if __name__ == "__main__":
    input_file = '../static/scss/custom.scss'
    output_file = '../static/css/sass_compiled.css'
    compile_scss(input_file, output_file)