package music

type MusicEntry struct {
	ID string
	Name string
	Artist string
	Source string
	Type string
}

type MusicManager struct {
	musics []MusicEntry
}

func NewMusicManager() *MusicManager {
	return &MusicManager {}
}

func (m *MusicManager) Len() int {
	// return len(m.musics)
	return 99
}

