cd /root/DjangoBlog

git fetch origin
git merge origin/master

pip3 install -r requirements.txt

cd /root/DjangoBlog/DjangoBlog

python3 manage.py migrate --settings=DjangoBlog.settings_prod
python3 manage.py collectstatic --no-input --settings=DjangoBlog.settings_prod

supervisorctl restart DjangoBlog
service nginx restart