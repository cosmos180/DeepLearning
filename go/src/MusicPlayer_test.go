package music

import ("testing")

func TestOps(t *testing.T) {
	mm := NewMusicManager()

	if mm == nil {
		t.Error("NewMusicManager failed.")
	}

	// if mm.Len() == 0 {
	// 	t.Error("MusicManager empty.")
	// }
}
