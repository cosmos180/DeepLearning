package kibana

import (
	"testing";
	"fmt"
)

func TestQueryAllOnlineDevices(t *testing.T) {
	tests := []struct {
		name string
	}{
		// TODO: Add test cases.
		{"hello"},
		{"world"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			fmt.Println(tt.name)
			QueryAllOnlineDevices()
		})
	}
}
