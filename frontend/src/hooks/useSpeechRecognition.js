/**
 * hooks/useSpeechRecognition.js — Browser Web Speech API wrapper
 * Supports: voice input + text-to-speech output
 */

import { useEffect, useRef, useState, useCallback } from "react";

// ── Speech Input (STT) ────────────────────────────────────────────────────────
export function useSpeechRecognition({ onResult, lang = "en-US" } = {}) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const recRef = useRef(null);

  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    setIsSupported(true);

    const rec = new SR();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = lang;

    rec.onresult = (e) => {
      const text = e.results[0][0].transcript;
      onResult?.(text);
    };
    rec.onerror = () => setIsListening(false);
    rec.onend = () => setIsListening(false);

    recRef.current = rec;
    return () => {
      rec.onresult = null;
      rec.onerror = null;
      rec.onend = null;
      try { rec.stop(); } catch {}
    };
  }, [lang, onResult]);

  const start = useCallback(() => {
    if (!recRef.current || isListening) return;
    try { recRef.current.start(); setIsListening(true); } catch {}
  }, [isListening]);

  const stop = useCallback(() => {
    if (!recRef.current) return;
    recRef.current.stop();
    setIsListening(false);
  }, []);

  return { isSupported, isListening, start, stop };
}

// ── Text-to-Speech (TTS) ──────────────────────────────────────────────────────
export function useTextToSpeech() {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isSupported] = useState(() => "speechSynthesis" in window);
  const utterRef = useRef(null);

  const speak = useCallback((text, lang = "en-US") => {
    if (!isSupported || !text) return;
    window.speechSynthesis.cancel();

    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = lang;
    utter.rate = 0.95;
    utter.pitch = 1;
    utter.volume = 1;

    utter.onstart = () => setIsSpeaking(true);
    utter.onend = () => setIsSpeaking(false);
    utter.onerror = () => setIsSpeaking(false);

    utterRef.current = utter;
    window.speechSynthesis.speak(utter);
  }, [isSupported]);

  const stop = useCallback(() => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, []);

  return { isSupported, isSpeaking, speak, stop };
}
