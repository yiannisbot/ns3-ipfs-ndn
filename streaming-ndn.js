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
var received = 0;

//var stream = fs.createWriteStream("video.mp4");
var loadedTime=0,loadedMaxTime=0,bufferedTime=30000;
var loaderContext, loaderConfig, loaderCallbacks;
var lastTime=0,tickTime=100;
var stopped = false;

var loadsuccess = function (name) {
	console.log("Load success "+name);
	//console.log('stats : %j', response.data.length+" "+performanceNow());
	//stream.write(response.data);
	if(loadedTime==0)loadedTime=performanceNow();

	loadedMaxTime+=durations[received]*1000;

	received++;
	//doTick();
	if(received<frags.length) {
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
    console.log("Play time "+playTime+ " "+loadedMaxTime)
	if(stopped){
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
	}
}

function getFile(name,callback)
{
    exec("ndncatchunks /video/"+name+" > "+name , function (error, stdout, stderr) {
         //sys.print('stdout: ' + stdout);
         //sys.print('stderr: ' + stderr);
         if (error !== null) {
         console.log('exec error: ' + error);
         }
         callback(name);
         console.log("out:"+stdout);
         console.log("err:"+stderr);
         });
}



function run() {
  setInterval(doTick, 1000);
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
                      console.log("Get file "+frags[received]);
                       getFile(frags[received],loadsuccess)
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



