#!/bin/bash
CONTAINER_ID=$1
docker exec $CONTAINER_ID apt-get update
docker exec $CONTAINER_ID apt-get -y install libsystemd-journal0 libapparmor1 sshpass openssh-client cpanminus  libsasl2-dev python-dev libldap2-dev libssl-dev sqlite3 python3-pip
docker exec $CONTAINER_ID pip3 install python-daemon
docker exec $CONTAINER_ID cpanm JSON DBI DBD::SQLite
docker exec $CONTAINER_ID /galaxy_venv/bin/pip install python-ldap
docker cp user.sqlite3 $CONTAINER_ID:/user.sqlite3
docker cp job_ids_record.sqlite3 $CONTAINER_ID:/tmp/remove_deteted_jobs/job_ids_record.sqlite3
docker exec $CONTAINER_ID chown -R galaxy:galaxy /tmp/remove_deleted_jobs
docker cp auth_conf.xml.sample $CONTAINER_ID:/export/galaxy-central/config/auth_conf.xml.sample
docker exec $CONTAINER_ID mkdir /tmp/remove_deleted_jobs
docker cp remove_deleted_jobs.py $CONTAINER_ID:/tmp/remove_deleted_jobs/remove_deleted_jobs.py
docker exec $CONTAINER_ID sed -i -e "s/<\/toolbox>//" /export/galaxy-central/config/tool_conf.xml.sample
docker exec -it $CONTAINER_ID perl -e '\
open OUT, ">>/export/galaxy-central/config/tool_conf.xml.sample";\
print OUT "  <section id=\"migap\" name=\"MiGAP\">\n";\
print OUT "    <tool file=\"migap/mga.xml\" />\n";\
print OUT "    <tool file=\"migap/trnascan-se.xml\" />\n";\
print OUT "    <tool file=\"migap/rnammer.xml\" />\n";\
print OUT "    <tool file=\"migap/16srrna-search.xml\" />\n";\
print OUT "    <tool file=\"migap/merge.xml\" />\n";\
print OUT "    <tool file=\"migap/cog-search.xml\" />\n";\
print OUT "    <tool file=\"migap/refseq-search.xml\" />\n";\
print OUT "    <tool file=\"migap/fa4tr.xml\" />\n";\
print OUT "    <tool file=\"migap/trembl-search.xml\" />\n";\
print OUT "    <tool file=\"migap/merge-a.xml\" />\n";\
print OUT "  </section>\n";\
print OUT "</toolbox>\n";\
close OUT;'
docker exec $CONTAINER_ID sudo -u galaxy git clone https://github.com/code-lab-0/migap_usegalaxy_tools.git
docker exec $CONTAINER_ID sh -c 'mv migap_usegalaxy_tools tools/migap'
docker exec $CONTAINER_ID /bin/docker pull yookuda/mga
docker exec $CONTAINER_ID /bin/docker pull yookuda/rnammer-1.2:1.0
docker exec $CONTAINER_ID /bin/docker pull yookuda/trnascan_se
docker exec $CONTAINER_ID /bin/docker pull yookuda/blast_plus
docker exec $CONTAINER_ID /bin/docker pull yookuda/merge
docker exec $CONTAINER_ID /bin/docker pull yookuda/fa4tr
docker exec $CONTAINER_ID /bin/docker pull yookuda/merge_a
