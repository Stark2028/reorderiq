import { useEffect, useState } from 'react';
import { getJson } from './lib';

type ResourceState<T> = {
  key: string | null;
  status: 'loading' | 'success' | 'error';
  data?: T;
  error?: string;
};

export function useResource<T>(key: string | null, revision = 0) {
  const [state, setState] = useState<ResourceState<T>>({ key: null, status: 'loading' });
  useEffect(() => {
    if (!key) return;
    let active = true;
    const controller = new AbortController();
    setState({ key, status: 'loading' });
    getJson<T>(key, controller.signal).then(
      (data) => {
        if (active) setState({ key, status: 'success', data });
      },
      (error) => {
        if (active && error.name !== 'AbortError')
          setState({ key, status: 'error', error: error.message });
      },
    );
    return () => {
      active = false;
      controller.abort();
    };
  }, [key, revision]);
  // Invalidate synchronously on a render with new controls, before effects run.
  const current = Boolean(key && state.key === key);
  return {
    data: current && state.status === 'success' ? state.data : undefined,
    error: current && state.status === 'error' ? state.error : undefined,
    loading: Boolean(key) && (!current || state.status === 'loading'),
    key: current ? state.key : null,
  };
}

export function useDebounced<T>(value: T, delay = 220) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

export function useMedia(query: string) {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches);
  useEffect(() => {
    const media = window.matchMedia(query);
    const change = () => setMatches(media.matches);
    change();
    media.addEventListener('change', change);
    return () => media.removeEventListener('change', change);
  }, [query]);
  return matches;
}
