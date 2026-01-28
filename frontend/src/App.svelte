<script>
  import { onMount } from "svelte";
  import { Scan, SelectFolder } from "../wailsjs/go/main/App";
  import FileTree from "./lib/components/FileTree.svelte";
  import {
    RefreshCw,
    FolderSearch,
    Minimize2,
    Maximize2,
    ArrowUp,
    ArrowDown,
  } from "lucide-svelte";

  let currentPath = "";
  let rootNode = null;
  let statusMessage = "Please select a folder to analyze";
  let isScanning = false;
  let errorMsg = null;
  let scanTime = 0;

  // Sorting state
  let sortField = "size"; // 'name', 'size', 'fileCount', 'percentage'
  let sortDirection = "desc"; // 'asc', 'desc'

  async function handleSelectFolder() {
    try {
      const path = await SelectFolder();
      if (path && path.length > 0) {
        startScan(path);
      }
    } catch (err) {
      statusMessage = "Error selecting folder: " + err;
    }
  }

  async function startScan(path) {
    if (!path) return;

    currentPath = path;
    isScanning = true;
    errorMsg = null;
    rootNode = null;
    statusMessage = `Scanning ${path}...`;

    const startTime = performance.now();

    try {
      const result = await Scan(path);

      if (result.error) {
        errorMsg = result.error;
        statusMessage = `Error: ${result.error}`;
      } else {
        rootNode = result.root;
        const duration = ((performance.now() - startTime) / 1000).toFixed(2);
        statusMessage = `Analysis complete in ${duration}s. Found ${rootNode ? rootNode.fileCount : 0} files.`;
      }
    } catch (err) {
      errorMsg = err.toString();
      statusMessage = "Scan failed: " + err;
    } finally {
      isScanning = false;
    }
  }

  function handleRefresh() {
    if (currentPath) {
      startScan(currentPath);
    }
  }

  function toggleSort(field) {
    if (sortField === field) {
      sortDirection = sortDirection === "asc" ? "desc" : "asc";
    } else {
      sortField = field;
      sortDirection = "desc"; // Default to desc for new columns typically for sizes
      if (field === "name") sortDirection = "asc"; // Default name to asc
    }
  }
</script>

<main class="container">
  <div class="toolbar">
    <button on:click={handleSelectFolder} disabled={isScanning}>
      <div style="display: flex; gap: 8px; align-items: center;">
        <FolderSearch size={18} />
        Select Folder
      </div>
    </button>

    <button on:click={handleRefresh} disabled={!currentPath || isScanning}>
      <div style="display: flex; gap: 8px; align-items: center;">
        <RefreshCw size={18} class={isScanning ? "spin" : ""} />
        Refresh
      </div>
    </button>

    <!-- Future: Expland All / Collapse All -->
  </div>

  <!-- Header Row for Sorting -->
  <div class="header-row">
    <div class="col-name header-cell" on:click={() => toggleSort("name")}>
      Name
      {#if sortField === "name"}
        {#if sortDirection === "asc"}<ArrowUp size={14} />{:else}<ArrowDown
            size={14}
          />{/if}
      {/if}
    </div>
    <div class="col-size header-cell" on:click={() => toggleSort("size")}>
      Size
      {#if sortField === "size"}
        {#if sortDirection === "asc"}<ArrowUp size={14} />{:else}<ArrowDown
            size={14}
          />{/if}
      {/if}
    </div>
    <div
      class="col-percent header-cell"
      on:click={() => toggleSort("percentage")}
    >
      %
      {#if sortField === "percentage"}
        {#if sortDirection === "asc"}<ArrowUp size={14} />{:else}<ArrowDown
            size={14}
          />{/if}
      {/if}
    </div>
    <div class="col-files header-cell" on:click={() => toggleSort("fileCount")}>
      Files
      {#if sortField === "fileCount"}
        {#if sortDirection === "asc"}<ArrowUp size={14} />{:else}<ArrowDown
            size={14}
          />{/if}
      {/if}
    </div>
  </div>

  <div class="content">
    {#if isScanning}
      <div class="loading">
        <RefreshCw size={48} class="spin" />
        <p>Scanning folder structure...</p>
      </div>
    {:else if errorMsg}
      <div class="error-view">
        <p>⚠️ {errorMsg}</p>
      </div>
    {:else if rootNode}
      <FileTree node={rootNode} parentSize={0} {sortField} {sortDirection} />
    {:else}
      <div class="empty-state">
        <p>No folder selected</p>
        <button on:click={handleSelectFolder} style="margin-top: 1rem;"
          >Select Folder</button
        >
      </div>
    {/if}
  </div>

  <div class="status-bar">
    {statusMessage}
  </div>
</main>

<style>
  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  .loading,
  .empty-state,
  .error-view {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--secondary-color);
  }

  .error-view {
    color: #ff5555;
  }

  /* Header Styles */
  .header-row {
    display: flex;
    padding: 8px 16px 8px 0; /* Match content padding */
    border-bottom: 2px solid var(--border-color);
    background-color: var(--sidebar-bg);
    font-weight: 600;
    color: var(--text-color);
    font-size: 13px;
    margin-left: 1rem; /* Match content padding left */
    margin-right: 1rem;
  }

  .header-cell {
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
    user-select: none;
  }

  .header-cell:hover {
    color: var(--accent-color);
  }

  /* Ensure these match FileTree.svelte widths */
  .col-name {
    flex: 1;
    min-width: 200px;
    padding-left: 20px; /* Offset for expand icon space roughly */
  }

  .col-size {
    width: 100px;
    text-align: right;
    justify-content: flex-end;
    padding-right: 10px;
  }

  .col-percent {
    width: 120px; /* Matches FileTree */
    padding-right: 10px;
  }

  .col-files {
    width: 80px;
    text-align: right;
    justify-content: flex-end;
    padding-right: 10px;
  }
</style>
