python get_latebreaking_data.py

sed -i -e 's/<u>/\\underline\{/g' latebreaking_abstract.csv
sed -i -e 's/<\/u>/\}/g' latebreaking_abstract.csv
sed -i -e 's/<sup>/\\textsuperscript\{/g' latebreaking_abstract.csv
sed -i -e 's/<\/sup>/\}/g' latebreaking_abstract.csv
sed -i -e 's/\ \&\ /\ \\\&\ /g' latebreaking_abstract.csv
sed -i -e 's/\&E/\\\&E/g' latebreaking_abstract.csv
sed -i -e 's/A\&/A\\\&/g' latebreaking_abstract.csv
sed -i -e 's/\_/\\\_/g' latebreaking_abstract.csv
sed -i -e 's/\\n\\n/\\linebreak/g' latebreaking_abstract.csv

# python concat_v1_latebreaking.py