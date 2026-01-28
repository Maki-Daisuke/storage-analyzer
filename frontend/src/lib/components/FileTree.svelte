<script>
  import { slide } from "svelte/transition";
  import {
    Folder,
    FolderOpen,
    File,
    ChevronRight,
    ChevronDown,
  } from "lucide-svelte";

  export let node;
  export let depth = 0;
  export let expanded = false;

  // Sorting props passed down from root
  export let sortField = "size"; // 'name', 'size', 'fileCount', 'percentage'
  export let sortDirection = "desc"; // 'asc', 'desc'

  // Parent size for percentage calculation.
  // If depth is 0, this node is root, so it represents 100% of itself (or we can pass null/0 to hide %)
  export let parentSize = 0;

  let isOpen = expanded;

  // Toggle folder open state
  function toggle() {
    if (node.type === "directory") {
      isOpen = !isOpen;
    }
  }

  // Format bytes to human readable string
  function formatSize(bytes) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB", "TB", "PB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  }

  // Calculate percentage
  $: percentage = parentSize > 0 ? (node.size / parentSize) * 100 : 100;
  $: percentageStr = parentSize > 0 ? percentage.toFixed(1) + "%" : "";

  // Sort children
  $: sortedChildren = node.children
    ? [...node.children].sort((a, b) => {
        let valA, valB;

        // Sort logic
        if (sortField === "name") {
          valA = a.name.toLowerCase();
          valB = b.name.toLowerCase();
        } else if (sortField === "size") {
          valA = a.size;
          valB = b.size;
        } else if (sortField === "fileCount") {
          valA = a.fileCount;
          valB = b.fileCount;
        } else if (sortField === "percentage") {
          // Percentage is proportional to size, so usually same as size sort
          valA = a.size;
          valB = b.size;
        }

        if (valA < valB) return sortDirection === "asc" ? -1 : 1;
        if (valA > valB) return sortDirection === "asc" ? 1 : -1;
        return 0;
      })
    : [];
</script>

<div class="node-container">
  <div
    class="node-row"
    on:click={toggle}
    class:is-folder={node.type === "directory"}
  >
    <!-- Name Column -->
    <div class="col-name" style="padding-left: {depth * 20}px">
      <span class="toggle-icon">
        {#if node.type === "directory"}
          {#if isOpen}
            <ChevronDown size={14} />
          {:else}
            <ChevronRight size={14} />
          {/if}
        {:else}
          <span style="width: 14px; display:inline-block;"></span>
        {/if}
      </span>

      <span class="icon">
        {#if node.type === "directory"}
          {#if isOpen}
            <FolderOpen size={16} color="#f9e2af" />
          {:else}
            <Folder size={16} color="#f9e2af" />
          {/if}
        {:else}
          <File size={16} color="#a6e3a1" />
        {/if}
      </span>
      <span class="name-text" title={node.name}>{node.name}</span>
      {#if node.error}<span class="error-badge" title={node.error}>⚠️</span
        >{/if}
    </div>

    <!-- Visual Bar (background) - optional enhancement could go here or using ::after on row -->

    <!-- Size Column -->
    <div class="col-size">{formatSize(node.size)}</div>

    <!-- Percentage Column -->
    <div class="col-percent">
      <div class="percent-bar-container">
        <div class="percent-bar" style="width: {percentage}%"></div>
        <span class="percent-text">{percentageStr}</span>
      </div>
    </div>

    <!-- Files Column -->
    <div class="col-files">{node.fileCount}</div>
  </div>
</div>

{#if isOpen && node.children}
  <div transition:slide|local={{ duration: 200 }}>
    {#each sortedChildren as child (child.path)}
      <svelte:self
        node={child}
        depth={depth + 1}
        parentSize={node.size}
        {sortField}
        {sortDirection}
      />
    {/each}
  </div>
{/if}

<style>
  .node-container {
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  .node-row {
    display: flex;
    align-items: center;
    padding: 4px 0;
    cursor: default;
    user-select: none;
    font-size: 13px;
    height: 32px;
  }

  .node-row:hover {
    background-color: var(--hover-color);
  }

  .is-folder {
    cursor: pointer;
  }

  /* Column Widths - Should match App.svelte header */
  .col-name {
    flex: 1; /* liquid width */
    display: flex;
    align-items: center;
    overflow: hidden;
    padding-right: 10px;
    min-width: 200px;
  }

  .col-size {
    width: 100px;
    text-align: right;
    padding-right: 10px;
    font-variant-numeric: tabular-nums;
    color: var(--text-color);
  }

  .col-percent {
    width: 120px;
    padding-right: 10px;
    display: flex;
    align-items: center;
  }

  .col-files {
    width: 80px;
    text-align: right;
    padding-right: 10px;
    color: var(--secondary-color);
    font-variant-numeric: tabular-nums;
  }

  .toggle-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    color: var(--secondary-color);
  }

  .icon {
    display: flex;
    align-items: center;
    margin-right: 8px;
  }

  .name-text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .error-badge {
    margin-left: 5px;
  }

  /* Percentage Bar */
  .percent-bar-container {
    width: 100%;
    height: 16px;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    position: relative;
    overflow: hidden;
  }

  .percent-bar {
    height: 100%;
    background-color: var(--accent-color);
    opacity: 0.7;
    border-radius: 2px;
  }

  .percent-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 10px;
    color: #fff;
    text-shadow: 0px 0px 2px rgba(0, 0, 0, 0.8);
    white-space: nowrap;
  }
</style>
