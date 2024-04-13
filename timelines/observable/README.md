[Active Projects](/projects/) 

# Observable

 The open static framework for D3 visualization generation and API Data Loaders.

Check out our implementation of [Observable Data Loaders](https://github.com/kargilthakur/Observables-DataLoader/tree/master/docs)

[Our Observable DataCommons](/data-commons/docs/) combo features Google's [International Data API](/data-pipeline/international/)

[Observable Framework](https://observablehq.com/framework/) is by Mike Bostock, the New York Times data scientist who created D3.

Mike Bostock provided assistance on [how to deploy to GitHub Pages](https://github.com/observablehq/framework/discussions/1030)
- Examples of deploy.yml files to use with [hello-framework install sample](https://observablehq.com/framework/)
- Without deploy.yml you can avoid broken pages by adding a .nojekyll file

<style>
table {
    display: block;
    width: 100%;
    width: max-content;
    max-width: 100%;
    overflow: auto;
    border: 1px solid #ccc;
}
table th {
	text-align: left;
	font-size: 16px;
	padding: 6px;
	border-bottom: 1px solid #ccc;
}
table td {
	padding: 6px;
}
</style>

| Command           | Description                                              |
| ----------------- | -------------------------------------------------------- |
| `yarn install`            | Install or reinstall dependencies                        |
| `yarn dev`        | Start local preview server                               |
| `yarn build`      | Build your static site, generating `./dist`              |
| `yarn deploy`     | Deploy your project to Observable                        |
| `yarn clean`      | Clear the local data loader cache                        |
| `yarn observable` | Run commands like `observable help`                      |

#### Dev Tips

1.) When coding, to see a new page in the sidebar, use Ctrl-C to stop the local server. Then use up arrow (↑) to re-run the command to start the preview server (npm run dev or yarn dev). Your browser should refresh.

2.) To view your dist folder, run the npx server at your "dist" folder and go to: http://127.0.0.1:8080
(Or you can run in the parent folder and add "dist" to the command.)

	npx http-server

Invoking a server with 'python -m http.server 8888' requires manually adding .html to side navigation link.

<br>

# Hello Framework - setup notes

You can avoid the following set steps by forking our [Observable DataCommons](https://github.com/ModelEarth/data-commons).

[Visualizing Common Goals](/data-commons/docs/) - placeholders for UN Sustainable Development Goals (SDGs)

## Setup steps we used

https://observablehq.com/framework/getting-started

**Add a new repo to GitHub using a cmd**
(These cmds are displayed when you say no README when creating a repo in GitHub.)

BUG: The final push step is not working. Probably needs a special login from the GitHub website. Also does not work when repo already added. Add how-to here.

	echo "# hello-framework" >> README.md
	git init
	git commit -m "first commit"
	git branch -M main
	git remote add origin https://github.com/ModelEarth/hello-framework.git
	git push -u origin main

**OR create a "hello-framework" repo first in GitHub.com**
Avoid adding a README file since you'll already have one locally.

This might only work if the repo was created with cmds above.
Run to deploy to the manually created repo.  Updates your local .git/config file.

	git remote add origin https://github.com/ModelEarth/hello-framework.git &&
	git branch -M main &&
	git push -u origin main

Third command resulted in error:

error: src refspec main does not match any  
error: failed to push some refs to 'https://github.com/ModelEarth/hello-framework.git'  
(base) helix@localhost hello-framework % 

So instead, rename the local folder and pull down a repo using GitHub Desktop.  
Copy everyting but the initial .git folder into the newly created repo.  
Remove dist/ from .gitignore file to deploy.  
Turn on GitHub Pages at the site root and view by including /dist in your URL.  
404 will appear at the root.

**Deploying via GitHub Actions**
You can schedule builds and deploy your project automatically on commit, or on a schedule.

Actions tab > Set up a workflow yourself

[deploy.yml](https://github.com/observablehq/framework/blob/main/.github/workflows/deploy.yml)


## Notes on Initial Install

Based on the [Observable Install Steps](https://observablehq.com/framework/getting-started#3.-publish)

IMPORTANT: Use Yarn if you are doing self-hosting on GitHub becauase deploy.yml is looking for yarn.lock.

In the webroot, we ran yarn because it's faster and more secure than: npm init @observablehq

	yarn create @observablehq

Yarn may prompt you to upgrade node. Check where you have node.

	where node

If you have two node instances, use both cmds to update. The second is for node version manager (nvm):

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

cd into the observable folder and run. This will open a browser at http://127.0.0.1:3001

	yarn dev

Or: npm run dev

Open a new terminal in the observable repo.
And build a static site for self hosting:

	yarn build

Or: npm run build


Command for sending a folder's content into the repo. [source](https://medium.com/@colleen85052/populate-github-repo-with-existing-folder-from-command-line-18fc67fb804d)
First you'll need to create an empty repo within GitHub.com.

<textarea class="codetext" rows="6">
git init
git add .
git commit -m "Init"
git remote add origin <link to repository, ending with ".git">
git remote -v
git push --set-upstream origin main
</textarea>

Commit changes (Edit the message)

<textarea class="codetext" rows="3">
git add .
git commit -m "Message goes Here"
git push
</textarea>

---

We might rename the "dist" folder to "io".
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

And the image and .js files return 404 with GitHub Pages at either of these:
https://model.earth/observable/dist/
https://model.earth/observable-dist/


Only works with the npx http-server command above.
This works when running the cmd in the parent, so this is not a level issue.
http://192.168.1.210:8082/dist/


To publish to Observable (You must be logged in to Observable to deploy.)

	yarn deploy



### Hello sample

Create a user account for yourself. Loren's test account:
[https://observablehq.com/@earthscape](https://observablehq.com/@earthscape)

Deployed project built above:

[earthscape.observablehq.cloud/hello-framework/](https://earthscape.observablehq.cloud/hello-framework/)

Kargil's demo-workspace project:
[https://demo-workspace.observablehq.cloud/hello-framework/](https://demo-workspace.observablehq.cloud/hello-framework/)

Change the visibility of your hosted project:

In your Observable account -> click "Viea All" go to projects list -> 3-dot menu to the right of your project name, choose Share and set Public to Can View.

Looks like we can add Public Notes (notebooks)
https://observablehq.com/@demo-workspace

But the project list itself is not visibly others, at least not without a paid account or maybe a setting change. I get 404 here:
https://observablehq.com/projects/@demo-workspace


### Hello sample - Self-Hosting Attempts

Our [observable self hosted test](https://github.com/ModelEarth/observable/) is built with the hello example, whereas [GordonSmith/framework](https://github.com/GordonSmith/framework) used a fork of the [framework website](https://github.com/observablehq/framework).


THE BIG QUESTION - How do we view unbroken static dist files using GitHub Pages?

How do we toggle deploy between deploying to self-hosting and to Observable? (This option seems to be bypassed duing the commands)

How do we run either of the following?
These are at the bottom here: [model.earth/observable](https://model.earth/observable/)

	yarn observable
	yarn observable help

If you are hosting on GitHub, do we turn on Github Pages?
What Actions do we need to add?

The answer is likely to be found in the [Observable Forum](https://talk.observablehq.com/).

We are following this post for a solution:
[Self Hosting post](https://talk.observablehq.com/t/announcing-observable-2-0/8744/8)
A reply links to a sample of forking the Observable website and its Github Actions.

Here's the action GordonSmith is using successfully (but what are the steps and settings?):
https://github.com/GordonSmith/framework/actions/runs/7920241316


Our attempt is failing:

We might need to figure out how to adjust the actions properly on the page above.
https://github.com/ModelEarth/framework/actions

The above is a fork of the Observable Framework repo, like GordonSmith did.
https://model.earth/framework/

This might have info on adding: feat: Deploy docs to github.io #1
https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site


Our self-hosting  Hello sample failed attempts:
[model.earth/observable/dist](https://model.earth/observable/dist/)
[model.earth/observable-dist](https://model.earth/observable-dist/)

Placing dist at the root of a site also fails:
[earthscape.github.io](https://earthscape.github.io/)

These steps didn't work yet:

Pages
Build and Deploy: Souce: GitHub Actions > create your own
Set the name to deploy-docs.yml 
Paste the text from [deploy-docs.yml](deploy-docs.yml) in the current folder
Also added deploy.yml

Still not working. Here are the failing actions, which were copied from GordonSmith/framework.
https://github.com/ModelEarth/observable/actions

<!--
New Workflow > Set up a workflow yourself
Copy
Deploy framework content to Pages
-->


## Added localsite repo as a submodule

This is neat because the Readme pages then appear in the left navigation.

Run in the docs folder: <!-- Or you can append "docs/" and run in repo's root. -->

git submodule add https://github.com/ModelEarth/localsite localsite && 
git commit -m "localsite submodule" && 

git submodule add https://github.com/ModelEarth/localsite apps && 
git commit -m "apps submodule"
