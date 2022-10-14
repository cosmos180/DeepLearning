package main

import (
	"fmt"
	"os"

	"tuputech.com/music"
)

func main() {
	fmt.Println("Hello world: ", os.Args[0])

	args := os.Args[1:]
	if args == nil || len(args) < 2 {
		fmt.Println("Param count < 2.")
	}

	fmt.Printf("example(1) = %d.\n", example(1))


	// ch := make(chan int, 1)
	// for {
	// 	select {
	// 		case ch <- 0:
	// 		case ch <- 1:
	// 		case ch <- 2:
	// 	}

	// 	i := <- ch
	// 	fmt.Println("Value received:", i)
	// }

	mm := music.NewMusicManager()

	if mm == nil {
		fmt.Println("NewMusicManager failed.")
	} else {
		fmt.Println("NewMusicManager success.")
		fmt.Println("music_player song count is ", mm.Len())
	}

	// kibana.QueryAllOnlineDevices()

	ch := make(chan int, 10)
	for {
		go channelTest(ch)

		i:= <-ch
		fmt.Println("Value received: ", i)
	}
}


func channelTest(ch chan int) {
	select {
	case ch <- 0:
	case ch <- 1:
	case ch <- 2:
	}
}

func example(x int) int  {
	if x == 0 {
		return 0
	} else {
		return 1
	}
}