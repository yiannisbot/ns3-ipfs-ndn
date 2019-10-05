'use strict'

/* global Hls Ipfs HlsjsIpfsLoader */
/* eslint-env browser */
//const HLS = require('hls-parser'); // For node
var m3u8 = require('m3u8');
var fs   = require('fs');
var exec = require('child_process').exec;
var fs = require('fs');
const date = require('log-timestamp');

var performanceNow = require("performance-now")
var frags = [];
var durations = [];
var requested=0,received = 0;

//var stream = fs.createWriteStream("video.mp4");
var startTime=0,loadedMaxTime=0,bufferSize=30000,bufferingTime=0,playTime=0;
var loaderContext, loaderConfig, loaderCallbacks;
var stopped = false;
var time = 0,loadedTime=0;
var lastTime=0,tickTime=1000,maxOnFly=5;
const hash=process.argv[2]
var loadsuccess = function (name,size) {
	var latency = performanceNow()-time;
	var throughput = (size*8*1000)/latency
	console.log("Load success "+name+" "+latency+" "+size+" "+throughput+" kbps");
	//console.log('stats : %j', response.data.length+" "+performanceNow());
	//stream.write(response.data);
    //console.log(response.url+" chunks: "+stats.chunk+" bytes: "+response.data.byteLength+" hashTime: "+stats.hashtime+" resolTime: "+stats.resoltime+" dTime: "+stats.dtime+" Totaltime: "+stats.totaltime+" totaltput: "+parseFloat(response.data.byteLength*8/(stats.totaltime)).toFixed(2)+" Kbps dloadtput: "+parseFloat(response.data.byteLength*8/(stats.dtime)).toFixed(2)+" Kbps");

	if(loadedTime==0)loadedTime=performanceNow();

	loadedMaxTime+=durations[received]*1000;
    if(startTime==0&&loadedMaxTime>=bufferSize)startTime=performanceNow();

	received++;
	//doTick();
	/*if(received<frags.length) {
		let playTime = performanceNow()-loadedTime;
		//console.log("Play2 time "+playTime + " " + loadedMaxTime)
		if(loadedMaxTime-playTime<bufferedTime) {
			console.log("Load "+frags[received])
	  		getFile(frags[received],loadsuccess)
		} else {
			stopped = true;	
		}
	} else {
		//stream.end();
        process.exit();
		
	}*/
    if(received>=frags.length){
        //stream.end();
        console.log("Bufferingtime: "+bufferingTime)
        process.exit();
    }
   
};


function parsePlayList(playlist,callback){
	let parser = m3u8.createStream();
	  //const playlist = HLS.parse(file);
	  let file2   = fs.createReadStream(playlist);

	  file2.pipe(parser);

	  parser.on('item', function(item) {
	  // emits PlaylistItem, MediaItem, StreamItem, and IframeStreamItem
	  	//console.log(item)
		callback(item.properties.uri,item.properties.duration)

	  });

}


function doTick(){
    let playTime = performanceNow()-loadedTime;
    //console.log("Play time "+playTime+ " "+loadedMaxTime)
    /*	if(stopped){
		if(received<frags.length) {
			console.log("Play time "+playTime + " " + loadedMaxTime)
			if(loadedMaxTime-playTime<bufferedTime) {
				console.log("Load "+frags[received])
				//loaderContext = { url: frags[received], frag: null, responseType: 'arraybuffer', progressData: false };
		  		//loader.load(loaderContext,loaderConfig,loaderCallbacks);
                getFile(frags[received],loadsuccess)
				stopped=false;
			}
		} else {
			//stream.end();
			node.stop(error => {
			    if (error) {
			      return console.error('Node failed to stop cleanly!', error)
			    }
			    console.log('Node stopped!')
			    process.exit();
			})
		}
	}*/
    if(received>0&&loadedMaxTime>playTime)playTime+=tickTime;
    else bufferingTime+=tickTime;
    //console.log("Play time "+playTime+ " "+loadedMaxTime)
    if(requested<frags.length) {
        //console.log("Play time "+playTime + " " + loadedMaxTime+" "+requested+" "+received+" "+maxOnFly)
        if((playTime>0&&loadedMaxTime-playTime<bufferSize&&requested-received==0)||(playTime==0&&(requested-received)<maxOnFly)) {
            //console.log("Load "+frags[requested])
            //loaderContext = { url: frags[requested], frag: null, responseType: 'arraybuffer', progressData: false };
            time = performanceNow();
            /*requested++
            loader.load(loaderContext,loaderConfig,loaderCallbacks);*/
            requested++
            getFile(frags[received],loadsuccess)

        }
    }
}

function getFile(name,callback)
{
    exec("ipfs get "+hash+"/"+name+" >/dev/null" , function (error, stdout, stderr) {
         //sys.print('stdout: ' + stdout);
         //sys.print('stderr: ' + stderr);
         if (error !== null) {
         console.log('exec error: ' + error);
         }
	 //console.log(stderr)
	 var arr = stderr.split(" ")
	 //console.log(arr[4]);
         callback(name,arr[4]);
         //console.log("out:"+stdout);
         //console.log(stderr);
         });
}



function run() {
  setInterval(doTick, tickTime);
};


getFile("master.m3u8", function(name) {
        // use the return value here instead of like a regular (non-evented) return value
        
        parsePlayList(name,function(frag,duration) {
                      //console.log("Received "+frag+" "+duration)
            frags.push(frag)
            durations.push(duration)
            //console.log("Result " +frags[frags.length-1]+" "+durations[durations.length-1])
            if(frags.length==1){
               //loaderContext = { url: frags[0], frag: null, responseType: 'arraybuffer', progressData: false };
               //loader.load(loaderContext,loaderConfig,loaderCallbacks)
               //console.log("Get file "+frags[received]);
               getFile(frags[received],loadsuccess)
               requested++
               run();

            }
        });
        
});

/*while(true)
{
	if(performanceNow()>lastTime+tickTime) {
		console.log("Tick "+performanceNow())
		lastTime = performanceNow();
		if(frags.length>0)doTick();
	}
}*/



