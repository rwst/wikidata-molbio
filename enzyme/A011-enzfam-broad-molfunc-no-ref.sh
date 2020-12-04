cat query.tsv |sed 's+^.*statement/++g' |sed 's+\t.*++g' |sed 's/^Q\([0-9]*\)-/Q\1$/g' |sed 's+$+ P887 Q84423633+g'
