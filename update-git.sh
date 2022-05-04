echo "- Printing env to trequirements.txt"
pip freeze > requirements.txt

echo '- DONE'

git status
git add .
git commit -m '{$1}'
