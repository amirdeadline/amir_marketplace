/**
 * Google Docs Heading Navigator and Numbering Manager
 *
 * Features:
 * - Displays all document tabs and nested tabs.
 * - Displays Heading 1 through Heading 6.
 * - Navigates to headings.
 * - Adds hierarchical numbering.
 * - Removes hierarchical numbering.
 * - Processes the active tab or all tabs.
 *
 * Menu:
 * - Open Navigator → floating resizable modeless dialog
 * - Open Numbering Heading Tool → Docs sidebar
 *
 * This script must be bound to a Google Docs document.
 */

const HEADING_NAVIGATOR = {
  MENU_NAME: 'Heading Tools',
  SIDEBAR_TITLE: 'Heading Navigator',
  NUMBER_MARKER_PROPERTY: 'HEADING_NAVIGATOR_NUMBERED',
  DIALOG_SIZE_PROPERTY: 'HEADING_NAVIGATOR_DIALOG_SIZE',
  MAX_HEADING_LEVEL: 6,
  DEFAULT_DIALOG_WIDTH: 420,
  DEFAULT_DIALOG_HEIGHT: 640,
  MIN_DIALOG_WIDTH: 280,
  MAX_DIALOG_WIDTH: 900,
  MIN_DIALOG_HEIGHT: 360,
  MAX_DIALOG_HEIGHT: 900,
};


/**
 * Runs whenever the document is opened.
 */
function onOpen() {
  DocumentApp.getUi()
    .createMenu(HEADING_NAVIGATOR.MENU_NAME)
    .addItem('Open Navigator', 'showHeadingNavigator')
    .addItem(
      'Open Numbering Heading Tool',
      'showHeadingNumberingTool'
    )
    .addToUi();
}


/**
 * Runs once when the add-on is installed for the user.
 * Ensures the Heading Tools menu appears immediately.
 */
function onInstall(e) {
  onOpen(e);
}


/**
 * Builds the shared HTML UI for either display mode.
 *
 * @param {string} initialPanel "navigator" or "numbering".
 * @param {string} displayMode "dialog" or "sidebar".
 * @return {GoogleAppsScript.HTML.HtmlOutput} Evaluated HTML.
 */
function buildHeadingToolHtml_(initialPanel, displayMode) {
  const allowedPanels = ['navigator', 'numbering'];
  const selectedPanel = allowedPanels.includes(initialPanel)
    ? initialPanel
    : 'navigator';
  const selectedMode =
    displayMode === 'dialog' ? 'dialog' : 'sidebar';

  const template = HtmlService.createTemplateFromFile('Sidebar');

  // JSON encoding safely creates JavaScript values in Sidebar.html.
  template.initialPanel = JSON.stringify(selectedPanel);
  template.displayMode = JSON.stringify(selectedMode);

  return template.evaluate();
}


/**
 * Opens the Heading Navigator as a floating modeless dialog.
 *
 * Google Docs sidebars are locked to 300px, so the navigator uses a
 * modeless dialog whose width/height can be adjusted with the mouse.
 */
function showHeadingNavigator() {
  const size = getNavigatorDialogSize_();
  const html = buildHeadingToolHtml_('navigator', 'dialog')
    .setWidth(size.width)
    .setHeight(size.height);

  DocumentApp.getUi().showModelessDialog(html, 'Heading Navigator');
}


/**
 * Opens the Numbering Heading Tool in the Docs sidebar.
 */
function showHeadingNumberingTool() {
  const html = buildHeadingToolHtml_('numbering', 'sidebar')
    .setTitle('Heading Numbering Tool');

  DocumentApp.getUi().showSidebar(html);
}


/**
 * Returns the last saved navigator dialog size, or defaults.
 *
 * @return {{width: number, height: number}} Dialog size in pixels.
 */
function getNavigatorDialogSize_() {
  const defaults = {
    width: HEADING_NAVIGATOR.DEFAULT_DIALOG_WIDTH,
    height: HEADING_NAVIGATOR.DEFAULT_DIALOG_HEIGHT,
  };

  try {
    const raw = PropertiesService
      .getUserProperties()
      .getProperty(HEADING_NAVIGATOR.DIALOG_SIZE_PROPERTY);

    if (!raw) {
      return defaults;
    }

    const parsed = JSON.parse(raw);
    return {
      width: clampInteger_(
        parsed.width,
        HEADING_NAVIGATOR.MIN_DIALOG_WIDTH,
        HEADING_NAVIGATOR.MAX_DIALOG_WIDTH,
        defaults.width
      ),
      height: clampInteger_(
        parsed.height,
        HEADING_NAVIGATOR.MIN_DIALOG_HEIGHT,
        HEADING_NAVIGATOR.MAX_DIALOG_HEIGHT,
        defaults.height
      ),
    };
  } catch (error) {
    return defaults;
  }
}


/**
 * Persists the navigator dialog size after the user resizes it.
 *
 * @param {Object} rawSize Width/height from the client.
 * @return {{width: number, height: number}} Saved size.
 */
function saveNavigatorDialogSize(rawSize) {
  const size = {
    width: clampInteger_(
      rawSize && rawSize.width,
      HEADING_NAVIGATOR.MIN_DIALOG_WIDTH,
      HEADING_NAVIGATOR.MAX_DIALOG_WIDTH,
      HEADING_NAVIGATOR.DEFAULT_DIALOG_WIDTH
    ),
    height: clampInteger_(
      rawSize && rawSize.height,
      HEADING_NAVIGATOR.MIN_DIALOG_HEIGHT,
      HEADING_NAVIGATOR.MAX_DIALOG_HEIGHT,
      HEADING_NAVIGATOR.DEFAULT_DIALOG_HEIGHT
    ),
  };

  PropertiesService
    .getUserProperties()
    .setProperty(
      HEADING_NAVIGATOR.DIALOG_SIZE_PROPERTY,
      JSON.stringify(size)
    );

  return size;
}


/**
 * Returns the complete tab and heading tree to the sidebar.
 *
 * @return {Object} Navigation data.
 */
function getDocumentNavigation() {
  const doc = DocumentApp.getActiveDocument();
  const rootTabs = doc.getTabs();

  return {
    documentName: doc.getName(),
    activeTabId: doc.getActiveTab().getId(),
    tabs: rootTabs.map(tab => buildTabNavigation_(tab)),
    generatedAt: new Date().toISOString(),
  };
}


/**
 * Recursively builds navigation data for a tab.
 *
 * @param {GoogleAppsScript.Document.Tab} tab The tab.
 * @return {Object} Serialized tab data.
 */
function buildTabNavigation_(tab) {
  const tabData = {
    id: tab.getId(),
    title: tab.getTitle() || 'Untitled tab',
    index: tab.getIndex(),
    type: String(tab.getType()),
    headings: [],
    childTabs: [],
  };

  if (tab.getType() === DocumentApp.TabType.DOCUMENT_TAB) {
    const documentTab = tab.asDocumentTab();
    tabData.headings = collectHeadingsFromTab_(documentTab);
  }

  tabData.childTabs = tab
    .getChildTabs()
    .map(childTab => buildTabNavigation_(childTab));

  return tabData;
}


/**
 * Collects heading information from a document tab.
 *
 * The paragraph index is used as a temporary locator. The sidebar should be
 * refreshed after document structure changes.
 *
 * @param {GoogleAppsScript.Document.DocumentTab} documentTab Document tab.
 * @return {Object[]} Heading records.
 */
function collectHeadingsFromTab_(documentTab) {
  const body = documentTab.getBody();
  const paragraphs = body.getParagraphs();
  const headings = [];

  paragraphs.forEach((paragraph, paragraphIndex) => {
    const level = headingToLevel_(paragraph.getHeading());

    if (level === null) {
      return;
    }

    const text = paragraph.getText().trim();

    if (!text) {
      return;
    }

    headings.push({
      paragraphIndex,
      level,
      text,
      cleanText: stripKnownNumbering_(text),
    });
  });

  return headings;
}


/**
 * Moves the user's cursor to a selected heading.
 *
 * @param {string} tabId Target tab ID.
 * @param {number} paragraphIndex Paragraph index in the tab body.
 * @return {Object} Result.
 */
function navigateToHeading(tabId, paragraphIndex) {
  const doc = DocumentApp.getActiveDocument();
  const tab = doc.getTab(String(tabId));

  if (!tab) {
    throw new Error('The selected tab no longer exists. Refresh the navigator.');
  }

  if (tab.getType() !== DocumentApp.TabType.DOCUMENT_TAB) {
    throw new Error('The selected tab is not a document-content tab.');
  }

  const documentTab = tab.asDocumentTab();
  const paragraphs = documentTab.getBody().getParagraphs();
  const index = Number(paragraphIndex);

  if (
    !Number.isInteger(index) ||
    index < 0 ||
    index >= paragraphs.length
  ) {
    throw new Error(
      'The heading location has changed. Refresh the navigator and try again.'
    );
  }

  const paragraph = paragraphs[index];
  const level = headingToLevel_(paragraph.getHeading());

  if (level === null) {
    throw new Error(
      'The selected paragraph is no longer a heading. Refresh the navigator.'
    );
  }

  const position = documentTab.newPosition(paragraph, 0);
  doc.setCursor(position);

  return {
    success: true,
    tabId: String(tabId),
    paragraphIndex: index,
    headingText: paragraph.getText(),
  };
}


/**
 * Returns available headings for the "start numbering from" selector.
 *
 * @param {string} scope "active" or "all".
 * @return {Object[]} Headings.
 */
function getNumberingStartOptions(scope) {
  const doc = DocumentApp.getActiveDocument();
  const tabs = getTargetDocumentTabs_(doc, scope || 'all');
  const options = [];

  tabs.forEach(tabInfo => {
    const paragraphs = tabInfo.documentTab.getBody().getParagraphs();

    paragraphs.forEach((paragraph, paragraphIndex) => {
      const level = headingToLevel_(paragraph.getHeading());

      if (level === null) {
        return;
      }

      const text = paragraph.getText().trim();

      if (!text) {
        return;
      }

      options.push({
        key: `${tabInfo.tab.getId()}::${paragraphIndex}`,
        tabId: tabInfo.tab.getId(),
        tabTitle: tabInfo.tab.getTitle() || 'Untitled tab',
        paragraphIndex,
        level,
        text,
        label:
          `${tabInfo.tab.getTitle() || 'Untitled tab'} — ` +
          `H${level}: ${text}`,
      });
    });
  });

  return options;
}


/**
 * Adds hierarchical numbering to headings.
 *
 * Expected options:
 * {
 *   scope: "active" | "all",
 *   startMode: "beginning" | "selected",
 *   startKey: "tabId::paragraphIndex",
 *   separator: ".",
 *   suffix: " ",
 *   minimumLevel: 1,
 *   maximumLevel: 6,
 *   firstNumber: 1,
 *   resetPerTab: true,
 *   removeExistingNumbers: true,
 *   skipMissingParents: false
 * }
 *
 * @param {Object} rawOptions User options.
 * @return {Object} Operation result.
 */
function applyHeadingNumbering(rawOptions) {
  const options = normalizeNumberingOptions_(rawOptions);
  const doc = DocumentApp.getActiveDocument();
  const targetTabs = getTargetDocumentTabs_(doc, options.scope);

  let numberingStarted = options.startMode === 'beginning';
  let changedCount = 0;
  let skippedCount = 0;
  let processedHeadingCount = 0;
  const warnings = [];

  // Shared counters are used only when resetPerTab is disabled.
  let sharedCounters = new Array(HEADING_NAVIGATOR.MAX_HEADING_LEVEL).fill(0);

  targetTabs.forEach(tabInfo => {
    let counters = options.resetPerTab
      ? new Array(HEADING_NAVIGATOR.MAX_HEADING_LEVEL).fill(0)
      : sharedCounters;

    const tabId = tabInfo.tab.getId();
    const body = tabInfo.documentTab.getBody();
    const paragraphs = body.getParagraphs();

    paragraphs.forEach((paragraph, paragraphIndex) => {
      const level = headingToLevel_(paragraph.getHeading());

      if (level === null) {
        return;
      }

      const currentKey = `${tabId}::${paragraphIndex}`;

      if (
        !numberingStarted &&
        options.startMode === 'selected' &&
        currentKey === options.startKey
      ) {
        numberingStarted = true;

        // Numbering begins with a clean hierarchy at the selected heading.
        counters = new Array(HEADING_NAVIGATOR.MAX_HEADING_LEVEL).fill(0);

        if (!options.resetPerTab) {
          sharedCounters = counters;
        }
      }

      if (!numberingStarted) {
        skippedCount++;
        return;
      }

      if (
        level < options.minimumLevel ||
        level > options.maximumLevel
      ) {
        skippedCount++;
        return;
      }

      processedHeadingCount++;

      updateCounters_(
        counters,
        level,
        options.firstNumber,
        options.skipMissingParents
      );

      const numberParts = [];

      for (let index = options.minimumLevel - 1; index < level; index++) {
        const value = counters[index];

        if (value === 0 && options.skipMissingParents) {
          continue;
        }

        numberParts.push(value || options.firstNumber);
      }

      if (numberParts.length === 0) {
        skippedCount++;
        return;
      }

      const oldText = paragraph.getText();
      const cleanText = options.removeExistingNumbers
        ? stripKnownNumbering_(oldText)
        : oldText;

      if (!cleanText.trim()) {
        skippedCount++;
        return;
      }

      const numberText = numberParts.join(options.separator);
      const newText = `${numberText}${options.suffix}${cleanText}`;

      if (newText === oldText) {
        skippedCount++;
        return;
      }

      replaceParagraphTextPreservingBasicStyle_(paragraph, newText);
      changedCount++;
    });
  });

  if (
    options.startMode === 'selected' &&
    !numberingStarted
  ) {
    warnings.push(
      'The selected starting heading was not found in the chosen scope.'
    );
  }

  PropertiesService
    .getDocumentProperties()
    .setProperty(
      HEADING_NAVIGATOR.NUMBER_MARKER_PROPERTY,
      JSON.stringify({
        timestamp: new Date().toISOString(),
        separator: options.separator,
        suffix: options.suffix,
        scope: options.scope,
      })
    );

  return {
    success: true,
    changedCount,
    skippedCount,
    processedHeadingCount,
    warnings,
    message: `Numbered ${changedCount} heading(s).`,
  };
}


/**
 * Removes hierarchical numeric prefixes from headings.
 *
 * This removes common numeric prefixes such as:
 * 1 Heading
 * 1.2 Heading
 * 1-2-3 Heading
 * 1_2_3 Heading
 * 1 / 2 / 3 Heading
 *
 * @param {Object} rawOptions Removal options.
 * @return {Object} Result.
 */
function removeHeadingNumbering(rawOptions) {
  const options = rawOptions || {};
  const scope = options.scope === 'active' ? 'active' : 'all';
  const minimumLevel = clampInteger_(options.minimumLevel, 1, 6, 1);
  const maximumLevel = clampInteger_(options.maximumLevel, 1, 6, 6);

  if (minimumLevel > maximumLevel) {
    throw new Error('Minimum heading level cannot exceed maximum level.');
  }

  const doc = DocumentApp.getActiveDocument();
  const targetTabs = getTargetDocumentTabs_(doc, scope);

  let changedCount = 0;
  let skippedCount = 0;

  targetTabs.forEach(tabInfo => {
    const paragraphs = tabInfo.documentTab.getBody().getParagraphs();

    paragraphs.forEach(paragraph => {
      const level = headingToLevel_(paragraph.getHeading());

      if (
        level === null ||
        level < minimumLevel ||
        level > maximumLevel
      ) {
        return;
      }

      const oldText = paragraph.getText();
      const newText = stripKnownNumbering_(oldText);

      if (newText === oldText) {
        skippedCount++;
        return;
      }

      replaceParagraphTextPreservingBasicStyle_(paragraph, newText);
      changedCount++;
    });
  });

  return {
    success: true,
    changedCount,
    skippedCount,
    message: `Removed numbering from ${changedCount} heading(s).`,
  };
}


/**
 * Builds a list of target document tabs.
 *
 * @param {GoogleAppsScript.Document.Document} doc Active document.
 * @param {string} scope "active" or "all".
 * @return {Object[]} Tab and DocumentTab pairs.
 */
function getTargetDocumentTabs_(doc, scope) {
  if (scope === 'active') {
    const activeTab = doc.getActiveTab();

    if (activeTab.getType() !== DocumentApp.TabType.DOCUMENT_TAB) {
      throw new Error('The active tab does not contain document content.');
    }

    return [{
      tab: activeTab,
      documentTab: activeTab.asDocumentTab(),
    }];
  }

  const results = [];

  doc.getTabs().forEach(tab => {
    flattenDocumentTabs_(tab, results);
  });

  return results;
}


/**
 * Recursively flattens all document tabs.
 *
 * @param {GoogleAppsScript.Document.Tab} tab Current tab.
 * @param {Object[]} output Output array.
 */
function flattenDocumentTabs_(tab, output) {
  if (tab.getType() === DocumentApp.TabType.DOCUMENT_TAB) {
    output.push({
      tab,
      documentTab: tab.asDocumentTab(),
    });
  }

  tab.getChildTabs().forEach(childTab => {
    flattenDocumentTabs_(childTab, output);
  });
}


/**
 * Converts a ParagraphHeading enum to a numeric level.
 *
 * @param {GoogleAppsScript.Document.ParagraphHeading} heading Heading enum.
 * @return {number|null} Heading level.
 */
function headingToLevel_(heading) {
  const mapping = new Map([
    [DocumentApp.ParagraphHeading.HEADING1, 1],
    [DocumentApp.ParagraphHeading.HEADING2, 2],
    [DocumentApp.ParagraphHeading.HEADING3, 3],
    [DocumentApp.ParagraphHeading.HEADING4, 4],
    [DocumentApp.ParagraphHeading.HEADING5, 5],
    [DocumentApp.ParagraphHeading.HEADING6, 6],
  ]);

  return mapping.has(heading) ? mapping.get(heading) : null;
}


/**
 * Updates hierarchical counters.
 *
 * @param {number[]} counters Counter array.
 * @param {number} level Heading level.
 * @param {number} firstNumber Initial number.
 * @param {boolean} skipMissingParents Whether missing parent values remain zero.
 */
function updateCounters_(
  counters,
  level,
  firstNumber,
  skipMissingParents
) {
  const currentIndex = level - 1;

  if (counters[currentIndex] === 0) {
    counters[currentIndex] = firstNumber;
  } else {
    counters[currentIndex]++;
  }

  // Reset all child counters whenever a parent or sibling advances.
  for (
    let index = currentIndex + 1;
    index < counters.length;
    index++
  ) {
    counters[index] = 0;
  }

  // Fill missing parents unless the user explicitly requests otherwise.
  if (!skipMissingParents) {
    for (let index = 0; index < currentIndex; index++) {
      if (counters[index] === 0) {
        counters[index] = firstNumber;
      }
    }
  }
}


/**
 * Removes common heading numbering prefixes.
 *
 * Examples removed:
 * - "1 Heading"
 * - "1.2 Heading"
 * - "1.2.3. Heading"
 * - "1-2-3 - Heading"
 * - "1_2_3: Heading"
 * - "(1.2) Heading"
 *
 * It intentionally requires whitespace after the prefix to reduce accidental
 * removal from values such as "2026Roadmap".
 *
 * @param {string} text Heading text.
 * @return {string} Heading without a recognized numeric prefix.
 */
function stripKnownNumbering_(text) {
  if (!text) {
    return '';
  }

  let output = String(text);

  const patterns = [
    // Parenthesized numbering: (1), (1.2), (1-2-3)
    /^\s*\(\s*\d+(?:\s*[.\-_/]\s*\d+)*\s*\)\s+/,

    // Numbering with optional punctuation before required whitespace.
    // Examples: 1 , 1.2 , 1.2. , 1-2-3 - , 1_2_3:
    /^\s*\d+(?:\s*[.\-_/]\s*\d+)*(?:\s*[.:\-–—)])?\s+/,
  ];

  patterns.forEach(pattern => {
    output = output.replace(pattern, '');
  });

  return output.trimStart();
}


/**
 * Replaces a paragraph's text while retaining its paragraph-level formatting
 * and approximating the first character's text formatting.
 *
 * Complex mixed inline formatting inside a heading cannot be perfectly
 * reconstructed after complete replacement. Most headings use one style.
 *
 * @param {GoogleAppsScript.Document.Paragraph} paragraph Target paragraph.
 * @param {string} newText Replacement text.
 */
function replaceParagraphTextPreservingBasicStyle_(paragraph, newText) {
  const textElement = paragraph.editAsText();
  const oldText = textElement.getText();

  let firstCharacterAttributes = null;

  if (oldText.length > 0) {
    try {
      firstCharacterAttributes = textElement.getAttributes(0);
    } catch (error) {
      firstCharacterAttributes = null;
    }
  }

  textElement.setText(newText);

  if (
    firstCharacterAttributes &&
    newText.length > 0
  ) {
    try {
      textElement.setAttributes(
        0,
        newText.length - 1,
        firstCharacterAttributes
      );
    } catch (error) {
      // Paragraph heading style remains intact even if inline attributes fail.
    }
  }
}


/**
 * Validates and normalizes numbering options.
 *
 * @param {Object} rawOptions Untrusted client options.
 * @return {Object} Normalized options.
 */
function normalizeNumberingOptions_(rawOptions) {
  const input = rawOptions || {};

  const minimumLevel = clampInteger_(
    input.minimumLevel,
    1,
    6,
    1
  );

  const maximumLevel = clampInteger_(
    input.maximumLevel,
    1,
    6,
    6
  );

  if (minimumLevel > maximumLevel) {
    throw new Error('Minimum heading level cannot exceed maximum level.');
  }

  let separator =
    typeof input.separator === 'string'
      ? input.separator
      : '.';

  let suffix =
    typeof input.suffix === 'string'
      ? input.suffix
      : ' ';

  // Prevent excessively large or potentially confusing input.
  separator = separator.slice(0, 5);
  suffix = suffix.slice(0, 5);

  if (separator.length === 0) {
    separator = '.';
  }

  if (suffix.length === 0) {
    suffix = ' ';
  }

  const startMode =
    input.startMode === 'selected'
      ? 'selected'
      : 'beginning';

  if (
    startMode === 'selected' &&
    !String(input.startKey || '').includes('::')
  ) {
    throw new Error('Select a valid starting heading.');
  }

  return {
    scope: input.scope === 'active' ? 'active' : 'all',
    startMode,
    startKey: String(input.startKey || ''),
    separator,
    suffix,
    minimumLevel,
    maximumLevel,
    firstNumber: clampInteger_(input.firstNumber, 1, 9999, 1),
    resetPerTab: input.resetPerTab !== false,
    removeExistingNumbers: input.removeExistingNumbers !== false,
    skipMissingParents: input.skipMissingParents === true,
  };
}


/**
 * Restricts a value to an integer range.
 *
 * @param {*} value Input value.
 * @param {number} minimum Minimum.
 * @param {number} maximum Maximum.
 * @param {number} fallback Fallback.
 * @return {number} Valid integer.
 */
function clampInteger_(value, minimum, maximum, fallback) {
  const number = Number(value);

  if (!Number.isInteger(number)) {
    return fallback;
  }

  return Math.min(maximum, Math.max(minimum, number));
}