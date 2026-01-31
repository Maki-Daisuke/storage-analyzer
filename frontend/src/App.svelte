<script>
  import { onMount } from "svelte";
  import { Scan, SelectFolder } from "../wailsjs/go/main/App";
  import { EventsOn } from "../wailsjs/runtime/runtime";
  import FileTree from "./lib/components/FileTree.svelte";
  import {
    RefreshCw,
    FolderSearch,
    Minimize2,
    Maximize2,
    ArrowUp,
    ArrowDown,
  } from "lucide-svelte";
  import { selectedPath, expandedPaths } from "./lib/stores/fileTreeStore";
  import { OpenFile } from "../wailsjs/go/main/App";

  let currentPath = "";
  let rootNode = null;
  let statusMessage = "Please select a folder to analyze";
  let isScanning = false;
  let errorMsg = null;
  let scanTime = 0;
  let usePhysicalSize = false;

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
    selectedPath.set(null);
    expandedPaths.clear();

    const startTime = performance.now();
    let cancelListener = null;

    // Listen for progress events
    cancelListener = EventsOn("scan:progress", (count) => {
      statusMessage = `Scanning ${path}... Found ${count} files`;
    });

    try {
      const result = await Scan(path, usePhysicalSize);

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
      if (cancelListener) cancelListener();
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
      sortDirection = "desc";
      if (field === "name") sortDirection = "asc";
    }
  }

  // Keyboard Navigation
  function handleKeyDown(e) {
    if (!rootNode || isScanning) return;

    // Only handle if no other interactive element is focused (unlikely here but good practice)
    if (["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) return;

    if (
      !["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Enter"].includes(
        e.key,
      )
    ) {
      return;
    }

    e.preventDefault();

    const rows = Array.from(document.querySelectorAll(".node-row"));
    if (rows.length === 0) return;

    const currentIndex = rows.findIndex((row) =>
      row.classList.contains("selected"),
    );

    if (e.key === "ArrowDown") {
      if (currentIndex === -1) {
        selectRow(rows[0]);
      } else if (currentIndex < rows.length - 1) {
        selectRow(rows[currentIndex + 1]);
      }
      return;
    }

    if (e.key === "ArrowUp") {
      if (currentIndex > 0) {
        selectRow(rows[currentIndex - 1]);
      }
      return;
    }

    if (currentIndex === -1) return;
    const currentRow = rows[currentIndex];
    const path = currentRow.dataset.path;
    const type = currentRow.dataset.type;
    const isExpanded = currentRow.dataset.expanded === "true";

    if (e.key === "Enter") {
      OpenFile(path);
      return;
    }

    if (e.key === "ArrowRight") {
      if (type === "directory") {
        if (!isExpanded) expandedPaths.add(path);
      }
      return;
    }

    if (e.key === "ArrowLeft") {
      if (type === "directory" && isExpanded) {
        expandedPaths.delete(path);
      } else {
        // Select parent
        // Helper to find parent row based on DOM structure
        // Current row is in a container.
        // Container is sibling of parent row? No.
        // Structure:
        // Parent Container
        //   Parent Row
        //   Siblings Wrapper (div with slide)
        //     This Node Container

        const nodeContainer = currentRow.closest(".node-container");
        const siblingsWrapper = nodeContainer.parentElement;
        // Verify wrapper is the slide div (it has no class, but it's the only parent)
        if (siblingsWrapper) {
          const parentContainer = siblingsWrapper.previousElementSibling;
          if (
            parentContainer &&
            parentContainer.classList.contains("node-container")
          ) {
            const parentRow = parentContainer.querySelector(".node-row");
            if (parentRow) selectRow(parentRow);
          }
        }
      }
      return;
    }

    throw new Error("Unreachable code reached. Invalid key: " + e.key);
  }

  function selectRow(row) {
    const path = row.dataset.path;
    // Prevent redundant updates which might cause loops or excessive overhead
    if ($selectedPath === path) return;

    selectedPath.set(path);
    // Scroll into view logic
    // simple: row.scrollIntoView({block: 'nearest'});
    // better: custom logic to avoid sticky headers overlapping

    // Check if sticky header is present (App.svelte line 103)
    // The header-row height is approx 35px.

    const headerOffset = 40;
    const rect = row.getBoundingClientRect();
    const container = document.querySelector(".content");

    // Using standard scrollIntoView for now, might need tweaks
    row.scrollIntoView({ block: "nearest" });
  }
</script>

<svelte:window on:keydown={handleKeyDown} />

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

    <label class="checkbox-label">
      <input type="checkbox" bind:checked={usePhysicalSize} disabled={isScanning} />
      Calculate Size on Disk
    </label>

    <!-- Future: Expand All / Collapse All -->
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
