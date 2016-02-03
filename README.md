# jenkins-jobs-builder
This is plugin support in the Jenkins Job Builder tool available from OpenStack repo.
I've sent it to their code review system (https://review.openstack.org/#/c/275304/),
but for some reason, unknown to me, their Jenkins is rejecting it.

File: jjb-hockeyapp-publisher.py is the code snippet that must be added somewhere in
publisher.py which is under the following path: jjbdir/jenkins_jobs/module/.
For your convenience I've added an already editted version of the file with this
plugin inside.
