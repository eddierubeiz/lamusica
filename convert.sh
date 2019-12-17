#
# This will convert the file to myfile.midi.out.pdf, formatted for US letter.
# It will also save an output midi file that should give you an idea of the notes which will actually be played by the music box.
# ./convert.sh myfile.midi
#

python3 ./lamusica.py --box=teanola30 --mid=$1_out.midi --pdf=$1_out.pdf  $1