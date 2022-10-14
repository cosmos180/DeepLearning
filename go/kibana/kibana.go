package kibana

import (
	"bytes"
	"encoding/gob"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

type RawLogMsg struct {
	// fmt.Println(logJson["time"])
	// fmt.Println(logJson["msg"])
	// fmt.Println(logJson["versionName"])
	// fmt.Println(logJson["mac"])
	time string
	msg string
	version string
	mac string
}

func GetBytes(key interface{}) ([]byte, error) {
    var buf bytes.Buffer
    enc := gob.NewEncoder(&buf)
    err := enc.Encode(key)
    if err != nil {
        return nil, err
    }
    return buf.Bytes(), nil
}

func QueryAllOnlineDevices() {
	fmt.Println("Query is running...")

	var jsonStr = []byte(`{
		"size": 2,
		"query": {
			"bool": {
				"must": [
					{
						"match_all": {}
					},
					{
						"match_phrase": {
							"json.deviceId": {
								"query": "a8:3f:a1:30:11:16"
							}
						}
					},
					{
						"range": {
							"json.log.time": {
								"gte": 1647187200000,
								"lte": 1647273599999,
								"format": "epoch_millis"
							}
						}
					}
				],
				"filter": [],
				"should": [],
				"must_not": []
			}
		},
		"sort": [
			{
				"json.log.time": {
					"order": "desc",
					"unmapped_type": "boolean"
				}
			}
		]
	}`)
	
	urlStr := "http://172.26.2.85:24702/tupu-log-tpfaceaccess-*/_search"
	resp, err := http.Post(urlStr, "application/json", bytes.NewBuffer(jsonStr))
    if err != nil {
        fmt.Println(err)
        return
    }
    fmt.Println(resp.StatusCode)


	defer resp.Body.Close()
    bodyC, _ := ioutil.ReadAll(resp.Body)

    var rawJson map[string]interface{}
    err = json.Unmarshal(bodyC, &rawJson)
    if err != nil {
        fmt.Println(err)
        return
    }

	// fmt.Println(rawJson["hits"])

	// hitsByteArray, _ := GetBytes(rawJson["hits"])
	// fmt.Println([]byte(rawJson["hits"]))
		// v:=rawJson["hits"].type
	// var hitsJson map[string]interface{}
	// err = json.Unmarshal(rawJson["hits"], &hitsJson)
    // if err != nil {
    //     fmt.Println(err)
    //     return
    // }

	hitsJson := rawJson["hits"].(map[string]interface{})

		// fmt.Println(reflect.TypeOf(rawJson["hits"]))
	// var hitJsonMap map[string]interface{}
    // err = json.Unmarshal(hitsByteArray, &hitJsonMap)
    // if err != nil {
    //     fmt.Println(err)
    //     return
    // }
    // fmt.Println(hitsJson["hits"])

	hitArray := hitsJson["hits"].([]interface{})
	fmt.Println(len(hitArray))


	for _, value := range hitArray {
		hitJson := value.(map[string]interface{})
		sourceJson := hitJson["_source"].(map[string]interface{})
		jsonJson := sourceJson["json"].(map[string]interface{})
		logJson := jsonJson["log"].(map[string]interface{})

		fmt.Println(logJson["time"])
		fmt.Println(logJson["msg"])
		fmt.Println(logJson["versionName"])
		fmt.Println(logJson["mac"])

		var rawLogMsg RawLogMsg
		rawLogMsg.time = logJson["time"].(string)
		rawLogMsg.msg = logJson["msg"].(string)
		rawLogMsg.version = logJson["versionName"].(string)
		rawLogMsg.mac = logJson["mac"].(string)
	}

}