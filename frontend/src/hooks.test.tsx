import { act, cleanup, renderHook, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { useResource } from './hooks';

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: Error) => void;
  const promise = new Promise<T>((yes, no) => {
    resolve = yes;
    reject = no;
  });
  return { promise, resolve, reject };
}
const response = (value: unknown) => ({ ok: true, json: async () => value }) as Response;
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('current-query evidence', () => {
  it('withholds stale data immediately and ignores an obsolete request that finishes late', async () => {
    const first = deferred<Response>(),
      second = deferred<Response>();
    const fetcher = vi.fn().mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    vi.stubGlobal('fetch', fetcher);
    const hook = renderHook(({ key }) => useResource<{ buyer: number }>(key), {
      initialProps: { key: '/a' },
    });
    const firstSignal = fetcher.mock.calls[0][1].signal as AbortSignal;
    hook.rerender({ key: '/b' });
    expect(hook.result.current.data).toBeUndefined();
    expect(firstSignal.aborted).toBe(true);
    await act(async () => {
      second.resolve(response({ buyer: 2 }));
    });
    await waitFor(() => expect(hook.result.current.data?.buyer).toBe(2));
    await act(async () => {
      first.resolve(response({ buyer: 1 }));
    });
    expect(hook.result.current.data?.buyer).toBe(2);
  });

  it('removes successful old data when the new query fails, allowing a clean retry', async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(response({ buyer: 1 }))
      .mockRejectedValueOnce(new Error('Network unavailable'))
      .mockResolvedValueOnce(response({ buyer: 3 }));
    vi.stubGlobal('fetch', fetcher);
    const hook = renderHook(({ key, revision }) => useResource<{ buyer: number }>(key, revision), {
      initialProps: { key: '/a', revision: 0 },
    });
    await waitFor(() => expect(hook.result.current.data?.buyer).toBe(1));
    hook.rerender({ key: '/b', revision: 0 });
    await waitFor(() => expect(hook.result.current.error).toBe('Network unavailable'));
    expect(hook.result.current.data).toBeUndefined();
    hook.rerender({ key: '/b', revision: 1 });
    await waitFor(() => expect(hook.result.current.data?.buyer).toBe(3));
    expect(hook.result.current.error).toBeUndefined();
  });

  it('does not expose buyer details when the selection is cleared', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response({ buyer: 1 })));
    const hook = renderHook(
      ({ key }: { key: string | null }) => useResource<{ buyer: number }>(key),
      { initialProps: { key: '/buyer/1' as string | null } },
    );
    await waitFor(() => expect(hook.result.current.data?.buyer).toBe(1));
    hook.rerender({ key: null });
    expect(hook.result.current.data).toBeUndefined();
    expect(hook.result.current.loading).toBe(false);
  });

  it('surfaces a readable server rejection instead of treating it as an empty queue', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({ detail: 'Experiment unavailable' }),
      }),
    );
    const hook = renderHook(() => useResource('/api/queue'));
    await waitFor(() => expect(hook.result.current.error).toBe('Experiment unavailable'));
    expect(hook.result.current.data).toBeUndefined();
  });
});
