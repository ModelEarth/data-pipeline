[Community Data](/community-data/) 

# Observable

[Observable Framework](https://observablehq.com/framework/) - for static site generation
Created by Mike Bostock, the New York Times data scientist who created D3.


## Notes on Initial Install

Based on the [Observable Install Steps](https://observablehq.com/framework/getting-started#3.-publish)

In the webroot, we ran yarn because it's faster and more secure than: npm init @observablehq

	yarn create @observablehq

Yarn may prompt you to upgrade node. Check where you have node.

	where node

If you have two node instances, use both cmds to update. The second is for node version manager (vvm):

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

And the image and .js files return 404 with GitHub Pages at either of these:
https://model.earth/observable/dist/
https://model.earth/observable-dist/


Only works with the npx http-server command above.
This works when running the cmd in the parent, so this is not a level issue.
http://192.168.1.210:8082/dist/


To publish to Observable (You must be logged in to Observable to deploy.)

	yarn deploy

Trying to use GitHub Desktop instead.
If you are hosting on GitHub, remember to turn on Github Pages.

THE BIG QUESTION - How do we view unbroken static dist files using GitHub Pages?

How do we toggle deploy between self-hosting and deploying to Observable?

How do we run either of the following?
These are at the bottom here: [model.earth/observable](https://model.earth/observable/)

	yarn observable
	yarn observable help


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



### Hello sample

Our [observable self hosted test](https://github.com/ModelEarth/observable/) is built with the hello example, whereas [GordonSmith/framework](https://github.com/GordonSmith/framework) used a fork of the [framework website](https://github.com/observablehq/framework).


Our Hello sample failed attempts:
[model.earth/observable/dist](https://model.earth/observable/dist/)
[model.earth/observable-dist](https://model.earth/observable-dist/)

Placing dist at the root of a site also fails:
[earthscape.github.io](https://earthscape.github.io/)

So far, only works for us when deploying to observable hosting:

[earthscape.observablehq.cloud/hello-framework/example-report](https://earthscape.observablehq.cloud/hello-framework/example-report)

Create a user account for yourself. We test with:
[https://observablehq.com/@earthscape](https://observablehq.com/@earthscape)



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
