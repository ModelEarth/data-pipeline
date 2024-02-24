[Community Data](/community-data/) 

# Observable

[Observable Framework](https://observablehq.com/framework/) - for static site generation
By Mike Bostock, New York Times data scientist who created D3.


## Notes on Initial Install

Based on the [Observable Install Steps](https://observablehq.com/framework/getting-started#3.-publish)

In the webroot, we ran yarn because it's faster and more secure than: npm init @observablehq

	yarn create @observablehq

Yarn may prompt you to upgrade node. Check where you have node.

	where node

If you have two node locations, use both cmds to update. The second is for node version manager:

	n latest
	nvm install node --reinstall-packages-from=node


Include sample files to help you get started?
│  Yes, include sample files
│
◇  Install dependencies?
│  Yes, via yarn
│
◇  Initialize git repository?
│  Yes

cd into the observable folder and run

	yarn dev

Open a new terminal in the observable repo.
And build a static site for self hosting:

	yarn build

We'll rename the "dist" folder to "io".
Doing so allows us to avoid merge conflicts if we were to remove /dist from the .gitignore file.

IMPORTANT:
You will not able to view these using localsite.
The dist and io folder only work with an HTTP server pointed at the repo.

To preview your built site locally, 
you MUST use a local static HTTP server such as [http-server](https://github.com/http-party/http-server):

	npx http-server dist &&
	npx http-server io

Either of these will then work:
http://127.0.0.1:8081
http://192.168.1.210:8081

So you can't view the subfolders at:
[localhost:8887/observable/dist](http://localhost:8887/observable/dist/)

And the image and .js also don't display here with GitHub Pages at either of these:
https://model.earth/observable/dist/
https://model.earth/observable-dist/


Only works with the npx http-server command above
This works when running the cmd in the parent, so this is not a level issue.
http://192.168.1.210:8082/dist/

If you are hosting on GitHub, remember to turn on Github Pages.

To publish to Observable (Haven't done this yet. Used GitHub Desktop instead.):

	yarn deploy

THE BIG QUESTION - How do we deploy the files to GitHub Pages?

How do we toggle deploy between self-hosting and deploying to Observable?

How do we run either of the following?
These are at the bottom here: https://model.earth/observable/

	yarn observable
	yarn observable help




