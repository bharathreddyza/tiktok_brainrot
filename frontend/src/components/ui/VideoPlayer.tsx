import React, { useRef, useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Play, Pause, RotateCcw, Download } from 'lucide-react';

const VideoPlayer = ({ videoUrl }) => {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.src = videoUrl;
    }
  }, [videoUrl]);

  const togglePlay = () => {
    if (videoRef.current.paused) {
      videoRef.current.play();
      setIsPlaying(true);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  };

  const restartVideo = () => {
    videoRef.current.currentTime = 0;
    videoRef.current.play();
    setIsPlaying(true);
  };

  const downloadVideo = () => {
    const a = document.createElement('a');
    a.href = videoUrl;
    a.download = 'generated_video.mp4';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <video
        ref={videoRef}
        className="w-full rounded-lg shadow-lg"
        controls
      />
      <div className="flex justify-center mt-4 space-x-4">
        <Button onClick={togglePlay}>
          {isPlaying ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
          {isPlaying ? 'Pause' : 'Play'}
        </Button>
        <Button onClick={restartVideo}>
          <RotateCcw className="h-4 w-4 mr-2" />
          Restart
        </Button>
        <Button onClick={downloadVideo}>
          <Download className="h-4 w-4 mr-2" />
          Download
        </Button>
      </div>
    </div>
  );
};

export default VideoPlayer;