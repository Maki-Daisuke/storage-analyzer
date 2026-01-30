import { writable } from 'svelte/store';

// Store for the currently selected file path
export const selectedPath = writable(null);


// Store for the set of expanded folder paths
const { subscribe, set, update } = writable(new Set());
export const expandedPaths = {
    subscribe,
    add: (path) => update(n => {
        const s = new Set(n);
        s.add(path);
        return s;
    }),
    delete: (path) => update(n => {
        const s = new Set(n);
        s.delete(path);
        return s;
    }),
    toggle: (path) => update(n => {
        const s = new Set(n);
        if (s.has(path)) {
            s.delete(path);
        } else {
            s.add(path);
        }
        return s;
    }),
    has: (path) => {
        let hasPath = false;
        update(n => {
            hasPath = n.has(path);
            return n;
        });
        return hasPath; // Note: this is not reactive, use $expandedPaths.has(path) in components
    },
    clear: () => set(new Set())
};
