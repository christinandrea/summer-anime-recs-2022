from difflib import SequenceMatcher


sim = SequenceMatcher()

sim.set_seqs('one','One Piece : Red')

print(sim.ratio())