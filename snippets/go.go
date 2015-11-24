package main

import (
	"bytes"
	"fmt"
	"net/http"
	"net/url"
)

type flag struct {
	flags, service string
	teamID         int
}

func submit(flags flag) {

	apiUrl := "localhost:8080"
	//resource := ""
	data := url.Values{}
	data.Set("team", strconv.Itoa(flags.teamID))
	data.Add("service", flags.service)
	data.Add("flags", flags.flags)

	u, _ := url.ParseRequestURI(apiUrl)
	//u.Path = resource
	urlStr := fmt.Sprintf("%v", u)

	client := &http.Client{}
	r, _ := http.NewRequest("POST", urlStr, bytes.NewBufferString(data.Encode())) // <-- URL-encoded payload
	r.Header.Add("Authorization", "auth_token=\"XXXXXXX\"")
	r.Header.Add("Content-Type", "application/x-www-form-urlencoded")
	r.Header.Add("Content-Length", strconv.Itoa(len(data.Encode())))

	resp, _ := client.Do(r)
	fmt.Println(resp.Status)
}

func main() {
	go submit(flag{"FLAG", "SERVICE", 69})
}
