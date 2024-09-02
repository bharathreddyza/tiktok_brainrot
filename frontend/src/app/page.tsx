'use client'
import React, { useState, useRef,useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Play } from 'lucide-react'
import VideoPlayer from '../components/ui/VideoPlayer'; // Import the new VideoPlayer component

const API_URL = 'http://localhost:5000';

// const videoOptions = [
//   { id: 1, src: "/videos/video1.mp4", title: "Video 1" },
//   { id: 2, src: "/videos/video1.mp4", title: "Video 2" },
//   { id: 3, src: "/videos/video1.mp4", title: "Video 3" },
//   { id: 4, src: "/videos/video1.mp4", title: "Video 4" },
// ];

const voiceOptions = [
  { id: 'en-GB-RyanNeural', name: 'Male Voice 1', sample: '/audio/test_audio_en-GB-RyanNeural.mp3' },
  // { id: 'male2', name: 'Male Voice 2', sample: '/audio/test_audio_en-US-AriaNeural.mp3' },
  { id: 'en-US-AriaNeural', name: 'Female Voice 1', sample: '/audio/test_audio_en-US-AriaNeural.mp3' },
  // { id: 'female2', name: 'Female Voice 2', sample: '/audio/test_audio_fr-FR-DeniseNeural.mp3' },
];

export default function Home() {
  const [inputType, setInputType] = useState<'text' | 'pdf'>('text');
  const [conversation, setConversation] = useState('');
  const [voice1, setVoice1] = useState(voiceOptions[0].id);
  const [voice2, setVoice2] = useState(voiceOptions[1].id);
  const [cta, setCta] = useState('');
  const [ctaHasAudio, setCtaHasAudio] = useState(false);
  const [ctaVoice, setCtaVoice] = useState(voiceOptions[0].id);
  const [pdf, setPdf] = useState<File | null>(null);
  const [selectedVideos, setSelectedVideos] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const videoRefs = useRef<(HTMLVideoElement | null)[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState<any>(null);
  const [videoOptions, setVideoOptions] = useState([]);
  const [videoType, setVideoType] = useState('syncAudio'); // added state variable

  const [youtubeUrl, setYoutubeUrl] = useState('');

const handleYoutubeUrlChange = (e) => {
  setYoutubeUrl(e.target.value);
};

const handleAddVideo = async () => {
  try {
    const response = await fetch(`${API_URL}/download_video`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ youtubeUrl }),
    });

    if (!response.ok) {
      throw new Error('Failed to download video');
    }

    // Handle the response as needed
  } catch (error) {
    console.error('Error downloading video:', error);
  }
};

useEffect(() => {
  const fetchVideoOptions = async () => {
    try {
      const response = await fetch(`${API_URL}/backgroundVideos`);
      const data = await response.json();
      console.log(data)
      const videoData = data.videos.map(video => {
        const binaryData = atob(video.blob);
        const arrayBuffer = new ArrayBuffer(binaryData.length);
        const uint8Array = new Uint8Array(arrayBuffer);

        for (let i = 0; i < binaryData.length; i++) {
          uint8Array[i] = binaryData.charCodeAt(i);
        }

        return {
          path: video.path,
          blob: new Blob([uint8Array], { type: 'video/mp4' }),
          url: URL.createObjectURL(new Blob([uint8Array], { type: 'video/mp4' })),
        };
      });
      setVideoOptions(videoData);
    } catch (error) {
      console.error('Error fetching video options:', error);
    }
  };

  fetchVideoOptions();
}, []);
  
const handleConversationChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
  setConversation(e.target.value);
  setInputType('text');
  setPdf(null);
};
  
  const playVoiceSample = (sampleSrc: string) => {
    if (audioRef.current) {
      audioRef.current.src = sampleSrc;
      console.log(sampleSrc)
      audioRef.current.play();
    }
  };

  const VoiceSelect = ({ value, onChange, label }: { value: string; onChange: (value: string) => void; label: string }) => (
    <div className="flex-1">
      <Label htmlFor={`${label}-select`}>{label}</Label>
      <div className="flex items-center space-x-2">
        <Select value={value} onValueChange={onChange}>
          <SelectTrigger className="flex-grow">
            <SelectValue placeholder="Select voice" />
          </SelectTrigger>
          <SelectContent>
            {voiceOptions.map(voice => (
              <SelectItem key={voice.id} value={voice.id}>{voice.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          size="icon"
          variant="outline"
          onClick={() => playVoiceSample(voiceOptions.find(v => v.id === value)?.sample || '')}
        >
          <Play className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );

  const handleCtaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCta(e.target.value);
  };

  const handlePdfUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0];
      setPdf(file);
      setInputType('pdf');
      setConversation('');

    //   const formData = new FormData();
    //   formData.append('file', file);

    //   try {
    //     const response = await fetch(`${API_URL}/pdf-extractor`, {
    //       method: 'POST',
    //       body: formData,
    //     });

    //     if (!response.ok) {
    //       throw new Error('Failed to extract text from PDF');
    //     }

    //     const data = await response.json();
    //     setConversation(data.text.join('\n'));
    //   } catch (error) {
    //     console.error('Error extracting text from PDF:', error);
    //     setError('Failed to extract text from PDF');
    //   }
    }
  };


  const handleVideoSelect = (index: number, video: any) => {
    setSelectedVideos(prev => {
      if (prev.some(video => video.index === index)) {
        return prev.filter(video => video.index !== index);
      } else if (prev.length < 4) {
        return [...prev, { index, path: video.path, url: video.url }];
      }
      return prev;
    });
  };
  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    const formData = new FormData();

    formData.append('voice1', voice1);
    formData.append('voice2', voice2);
    formData.append('cta', cta);
    formData.append('ctaHasAudio', ctaHasAudio.toString());
    formData.append('ctaVoice', ctaHasAudio ? ctaVoice : '');
    formData.append('videoIds', JSON.stringify(selectedVideos));
    formData.append('type', videoType);

    if (inputType === 'text') {
      formData.append('conversation', conversation);
    } else if (inputType === 'pdf' && pdf) {
      formData.append('pdf', pdf);
    }

    console.log('Form Data:');
    for (let [key, value] of formData.entries()) {
      console.log(key, value);
    }

    try {
      const response = await fetch(`${API_URL}/conversation`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process the request');
      }
      
      const blob = await response.blob();
      const videoUrl = URL.createObjectURL(blob);
      setGeneratedVideoUrl(videoUrl);

    } catch (error) {
      console.error('Error submitting data:', error);
      setError('Failed to submit data to the server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="w-full max-w-4xl space-y-6">
        <h1 className='text-3xl font-bold tracking-tight'>BRAIN ROT ENGINE</h1>
        <Select value={inputType} onValueChange={(value: 'text' | 'pdf') => setInputType(value)}>
        <SelectTrigger className="flex-grow">
          <SelectValue placeholder="Select input type" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="text">Text Conversation</SelectItem>
          <SelectItem value="pdf">PDF Upload</SelectItem>
        </SelectContent>
      </Select>

        <Card>
          <CardContent className="p-6 space-y-4">
            <div>
              <Label htmlFor="conversation-input">Enter Conversation</Label>
              <textarea
                id="conversation-input"
                className="w-full p-2 border rounded"
                value={conversation}
                onChange={handleConversationChange}
                rows={4}
              />
            </div>

            <div>
            <Label htmlFor="video-type-select">Video Type</Label>
            <Select value={videoType} onValueChange={setVideoType}>
              <SelectTrigger className="flex-grow">
                <SelectValue placeholder="Select video type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="syncAudio">Sync Audio</SelectItem>
                <SelectItem value="messageBubble">Message Bubble</SelectItem>
              </SelectContent>
            </Select>
          </div>
         
         
            <div className="flex space-x-4">
            <VoiceSelect value={voice1} onChange={setVoice1} label="Voice for Person 1" />
            <VoiceSelect value={voice2} onChange={setVoice2} label="Voice for Person 2" />
            </div>
            <div>
              <Label htmlFor="cta-input">Enter CTA</Label>
              <Input
                id="cta-input"
                type="text"
                value={cta}
                onChange={handleCtaChange}
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="cta-audio-checkbox"
                checked={ctaHasAudio}
                onCheckedChange={(checked) => setCtaHasAudio(checked as boolean)}
              />
              <Label htmlFor="cta-audio-checkbox">CTA has audio</Label>
            </div>
            {ctaHasAudio && (
                 <VoiceSelect value={ctaVoice} onChange={setCtaVoice} label="CTA Voice" />
            )}
            <div>
              <Label htmlFor="pdf-input">Upload PDF</Label>
              <Input
                id="pdf-input"
                type="file"
                accept=".pdf"
                onChange={handlePdfUpload}
              />
            </div>
          </CardContent>
        </Card>
        
 
         
  

        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-bold mb-4">Select Videos (1-4)</h2>
            <Card>
              <CardContent className="p-6">
                <h2 className="text-xl font-bold mb-4">Add Video from YouTube</h2>
                <Input
                  type="text"
                  value={youtubeUrl}
                  onChange={handleYoutubeUrlChange}
                  placeholder="Enter YouTube URL"
                />
                <Button onClick={handleAddVideo}>Add Video</Button>
              </CardContent>
            </Card>
            <div className="grid grid-cols-2 gap-4">
                      {videoOptions.map((video, index) => (
            <div
              key={video.path}
              className={`relative cursor-pointer ${selectedVideos.some(video => video.index === index) ? 'ring-2 ring-blue-500' : ''}`}
              onClick={() => handleVideoSelect(index,video)}
              onMouseEnter={() => videoRefs.current[index]?.play()}
              onMouseLeave={() => {
                if (videoRefs.current[index]) {
                  videoRefs.current[index]!.pause();
                  videoRefs.current[index]!.currentTime = 0;
                }
              }}
            >
              <video
                ref={el => videoRefs.current[index] = el}
                src={video.url}
                className="w-full h-auto"
                loop
                muted
                playsInline
              />
              {/* <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white">
                {`Video ${index + 1} - ${video.path}`}
              </div> */}
            </div>
          ))}
            </div>
          </CardContent>
        </Card>

        {error && <div className="text-red-500">{error}</div>}

        <Button 
          onClick={handleSubmit}
          disabled={loading || selectedVideos.length === 0 || (!conversation && !pdf) || !cta}
        >
          {loading ? 'Processing...' : 'Create'}
        </Button>
        {generatedVideoUrl && (
          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-bold mb-4">Generated Video</h2>
              <VideoPlayer videoUrl={generatedVideoUrl} />
            </CardContent>
          </Card>
        )}
      </div>
      <audio ref={audioRef} className="hidden" />

    </main>
  );
}