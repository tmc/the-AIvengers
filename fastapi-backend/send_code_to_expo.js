// index.js
const { Snack } = require('snack-sdk');
const fs = require('fs');

async function main() {

    // file-name input:
    const project_name = process.argv[2];

    // Load code from list of files
    var file_list = ["App.js"]

    // create dictionary with contents of the files
    var files = {}
    for (var i = 0; i < file_list.length; i++) {
        var file_name = file_list[i]
        var file_contents = fs.readFileSync(file_name, 'utf8');

        files[file_name] = {
            type: 'CODE',
            contents: file_contents,
        }
    }

    // Create Snack
    const snack = new Snack({
    user: { accessToken: "3mfgoz_Uulng9RU5Wp8IYFw2LJ-cc0aWadPsFJs4"},
    name: project_name,
    description: 'Generated by the AIvenger team! Have fun playing around with it :)',
    files: files,
    });

    await snack.saveAsync();

    // Make the Snack available online
    snack.setOnline(true);
    const { id, url } = await snack.getStateAsync();

    snack_url = "https://snack.expo.dev/" + id;
    console.log(snack_url)

    // Stop Snack when done
    snack.setOnline(false);
}

main().catch((error) => console.error('Error:', error));