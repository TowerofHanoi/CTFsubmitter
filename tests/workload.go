package main

import (
	"bytes"
	"fmt"
	"math/rand"
	"net/http"
	"net/url"
	"runtime"
	//	"os"
	"strconv"
	"time"
)

type flag struct {
	flags, service string
	teamID         int
}

func submit(flags flag) {

	apiUrl := "http://localhost:8080"
	data := url.Values{}
	data.Set("team", strconv.Itoa(flags.teamID))
	data.Add("service", flags.service)
	data.Add("flags", flags.flags)

	u, _ := url.ParseRequestURI(apiUrl)
	urlStr := fmt.Sprintf("%v", u)

	client := &http.Client{}
	r, _ := http.NewRequest("POST", urlStr, bytes.NewBufferString(data.Encode())) // <-- URL-encoded payload
	r.Header.Add("Content-Type", "application/x-www-form-urlencoded")
	r.Header.Add("Content-Length", strconv.Itoa(len(data.Encode())))

	resp, err := client.Do(r)
	if err != nil {
		fmt.Println("something wen wrong:" + err.Error())
	} else {
		fmt.Println(resp.Status)
	}
}
func submitter(fps float64, dupfactor int, flagsChannel chan flag) {
	nanoseconds := int64(1000000.0 / fps)
	delay := time.Duration(nanoseconds) * time.Nanosecond
	tick := time.Tick(delay)
	for flags, ok := <-flagsChannel; ok; flags, ok = <-flagsChannel {
		submit(flags)
		_ = <-tick
		if rand.Int()%100 < dupfactor {
			flagsChannel <- flags
		}
	}
}
func generateFlags(flagslength, teams, services int, charset string, flagsChannel chan flag) {

	//do not fill channel! put only if len(flagsChannel) < max
	b := make([]byte, flagslength)
	for i := range b {
		b[i] = charset[rand.Int63()%int64(len(charset))]
	}
	newflag := string(b)
	team := rand.Int() % teams
	service := "Test Service " + strconv.Itoa(rand.Int()%services)
	flagsChannel <- flag{newflag, service, team}
}
func main() {
	/*flagslength, _ := strconv.Atoi(os.Args[1])
	dupfactor, _ := strconv.Atoi(os.Args[3])
	teams, _ := strconv.Atoi(os.Args[5])
	services, _ := strconv.Atoi(os.Args[4])
	submitters, _ := strconv.Atoi(os.Args[7])
	duration, _ := strconv.Atoi(os.Args[6])
	fps, _ := strconv.Atoi(os.Args[2])
	if len(os.Args) < 4 {
		fmt.Println(`
		Please provide:
		the flags length
		the flags per second
		the duplication factor(percentage of duplicated flags)
		the number of mock services
		the number of mock Teams
		the duration of the test in seconds
		the number of submitters
		`)
		return
	}*/
	threads := runtime.NumCPU() + runtime.NumCPU()/2
	runtime.GOMAXPROCS(threads)
	flagslength := 64
	dupfactor := 60 //%
	teams := 200
	services := 50
	submitters := 9
	duration := 60
	fps := 70

	rand.Seed(time.Now().UnixNano())
	flagsChannel := make(chan flag, 1000000)
	go generateFlags(flagslength, teams, services, "1234567890ACBDEF", flagsChannel)
	actualfps := float64(fps) / float64(submitters)
	for i := 0; i < submitters; i++ {
		go submitter(actualfps, dupfactor, flagsChannel)
	}
	dur := time.Duration(duration) * time.Second
	time.Sleep(dur)
	//	console := bufio.NewReader(os.Stdin)
	//	_, _ = console.ReadString('\n')

}
