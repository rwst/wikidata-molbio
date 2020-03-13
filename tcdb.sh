sed 's/^>gnl|TC-DB|//g' |sed '/^......[A-Z]/d'|sed 's/^\(......\s[A-Z0-9.]\+\)\s.*/\1/g' |sed '/^[A-Z]\+$/d' |sed '/.*\[.*/d'
