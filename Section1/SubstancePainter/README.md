The Substance painter projects here should only be saved when the baked texture maps have been deleted
and the size reduced to "128".

Otherwise, the project files are too big to check in and change too frequently. Once the layers have been
created, then delete the baked textures, set size to 128 and save and optimise/shrink project. Next time you are working
on this project, you can reset size to something large and rebake the textures derived from the mesh.

Note to do this you need to follow the process:

* Goto `Texture Set Settings / General Settings` and change the `Size` to 128
* Goto `Texture Set Settings` and delete all the `Mesh Maps`
* Click the menu item `File > Remove unused Resources...`
* Click the menu item `File > More save options > Save and reduce file size...`
