/**
 * @preserve
 * Wizard js
 * version 1.2.0
 * 2022.12.22--29
 * Miguel Gastelumendi -- mgd
*/
// @ts-check
/* cSpell:locale en, pt-br */

/**
 * This callback should return true to go
 * @callback fOnNext
 * @returns {boolean}
 */

/**
 * @typedef {Object} wzdControl
 * @property {Function} initPage
 * @property {Function} messageInfo
 * @property {Function} messageError
 * :
 * :
 */

/**
 * @typedef {Object} wzdItem
 * @property {string} bodyId parent ID element of the buttons
 * @property {string} text buttons text, if nul/undef caption is used
 * @property {string} caption display on selection
 * @property {number} id item`s ID, if informed, it is sent as a parameter
 * @property {string} href address of the next page (if all items have the same one, use 'nextPage')
 * @property {string} fileName image file name and extension
 */

/**
 * @typedef {Object} wzdConfig
 * @property {Array<wzdItem>} data array of json items
 * @property {number} mode see wzdControl.mode
 * @property {fOnNext?} onNext callback on Next button
 * @property {string?} nextPage address of next page
 * @property {string?} path to wzdItem.fileName
 * @property {string?} [alignText = 'center'] buttons text alignment [center|start|end]
 * @property {boolean?} [multiSelect=false] allow selected item per group
 */

/**
 * @typedef {Object} groupItem
 * @property {string} bodyId the ID of the parent element (this is an 'index' to wzdConfig<wzdItem>.bodyId
 * @property {number} selected If multiSelect: select button ix or -1 : see selectedIx
 */

const wzdControl = {
  multiSelect: false,
  selectedItemIx: -1,
  nextPageHref: '',  // Wizard page has ony one target
  displayMode: 0,
  /** @type {Array<groupItem>}*/
  groups: [],
  /** @type {Array<wzdItem>} */
  jsoData: [],
  /** @type {fOnNext?} */
  fOnNext: null,

  ge: (/** @type {string} */ sId) => /** @type{HTMLElement} */(document.getElementById(sId)),
  getBtn: (/** @type {number} */ ix) => wzdControl.ge(wzdControl.getBtnId(ix)),
  getBtnId: (/** @type {number} */ ix) => `wzdBtn${ix}`,
  setBody: (/** @type {string} */ sId, /** @type {string} */ sBody) => wzdControl.ge(sId).innerHTML = '' + sBody,
  getColClasses: (/** @type {string} */ sBodyId) => {
    const w = wzdControl.jsoData.filter(itm => (itm.bodyId == sBodyId)).length;
    const sCols = 'row-cols-1' +
      (((w > 1) ? ' row-cols-sm-2' : '')) +
      (((w > 2) && (w & 1)) ? ' row-cols-md-3' : '') +  // ()> 2 && odd)
      (((w > 3) ? ' row-cols-lg-4' : ''));
    return sCols;
  },
  getSelectedCount: () => (wzdControl.multiSelect ? wzdControl.groups.filter(grp => (grp.selected >= 0)).length : ((wzdControl.selectedItemIx < 0) ? 0 : 1)),

  getGroupItemByIx: (/** @type {number} */ ix) => {
    const itm = wzdControl.jsoData[ix];
    return /** @type {groupItem} */(wzdControl.groups.find(grp => grp.bodyId == itm.bodyId));
  },

  //@ts-ignore mdlControl is defined on modal.js
  modalReady: () => (typeof mdlControl == 'object'),

  /** @private */
  showSelected: () => {
    const i = wzdControl.getSelectedCount();
    let sSelected = `Selecionado${((i == 1) ? '' : 's')}: <b>`;
    if (wzdControl.multiSelect) {
      sSelected += wzdControl.groups.filter(grp => grp.selected >= 0).map(grp => wzdControl.jsoData[grp.selected].caption).join(', ');
    } else {
      sSelected += wzdControl.jsoData[wzdControl.selectedItemIx].caption;
    }
    wzdControl.displaySelected(sSelected + '</b>');
  },
  /** @private */
  selectItem: (/** @type {number} */ ix) => {
    let iLastSelectedIx;
    let grp = {};
    if (wzdControl.multiSelect) {
      grp = wzdControl.getGroupItemByIx(ix);
      iLastSelectedIx = grp.selected;
    } else {
      iLastSelectedIx = wzdControl.selectedItemIx;
    }
    if (iLastSelectedIx == ix) { return; }


    let eleBtn = wzdControl.getBtn(ix);
    eleBtn.classList.remove('btn-info');
    eleBtn.classList.add('btn-warning');
    if (iLastSelectedIx >= 0) {
      eleBtn = wzdControl.getBtn(iLastSelectedIx);
      eleBtn.classList.remove('btn-warning');
      eleBtn.classList.add('btn-info');
    }
    // save
    if (wzdControl.multiSelect) {
      grp.selected = ix;
    } else {
      wzdControl.selectedItemIx = ix;
    }
    wzdControl.showSelected();

  },

  /** @private */
  display: () => {
    const aBody = []; // array with the IDs of each body (parent's ids)
    const aHtml = []; // HTML for each parent body
    wzdControl.jsoData.forEach(itm => { if (!itm.bodyId) itm.bodyId = 'idWzdBody' }); // default body's ID
    const _getBodyIx = (sBodyId, sOpenDiv) => {
      let id = aBody.indexOf(sBodyId);
      if (id < 0) {
        id = aBody.push(sBodyId) - 1;
        aHtml.push(sOpenDiv);
        wzdControl.groups.push({ bodyId: sBodyId, selected: -1 });
      }
      return id;
    }
    let bodyIx;
    let sAlign = 'text-' + wzdControl.alignText;
    switch (wzdControl.displayMode) {
      case wzdControl.mode.CUSTOM:
        return;
      case wzdControl.mode.BUTTONS:
        wzdControl.jsoData.forEach((itm, ix) => {
          bodyIx = _getBodyIx(itm.bodyId, '<div class="d-grid gap-2">');
          aHtml[bodyIx] +=
            `<button id="${wzdControl.getBtnId(ix)}" class="btn btn-info bg-gradient ${sAlign} mx-5" type="button" onclick="wzdControl.selectItem(${ix})">` +
            (itm.text ? itm.text : itm.caption) +
            '</button>';
        });
        break;
      case wzdControl.mode.IMAGES:
        wzdControl.jsoData.forEach((itm, ix) => {
          let onClick = `onclick="wzdControl.selectItem(${ix})`;
          bodyIx = _getBodyIx(itm.bodyId, `<div class="row ${wzdControl.getColClasses(itm.bodyId)}">`);
          aHtml[bodyIx] +=
            `<div class="col ${sAlign} mb-3">` +
            `<button id=${wzdControl.getBtnId(ix)} class="mb-2 btn btn-info bg-gradient" type="button" style="height:4.2em; width:100%" ${onClick}">` +
            (itm.text ? itm.text : itm.caption) +
            '</button>' +
            `<a ${onClick}"> <img src="${wzdControl.path}${itm.fileName}" alt="${itm.fileName ? itm.fileName : 'Imagem não disponível'}"></a>` +
            '</div>';
        });
        break;
      default:
        wzdControl.jsoData.forEach(itm => { _getBodyIx(itm.bodyId, '<div>'); });
    }
    aBody.forEach((sBodyId, i) => wzdControl.setBody(sBodyId, aHtml[i] + '</div>'));
  },

  /** @private */
  selectionReady: (o) => {
    let i;
    const k = wzdControl.groups.length;
    if (!wzdControl.multiSelect) {
      o.msg = 'Por favor, selecione uma das opções.';
      return (wzdControl.selectedItemIx >= 0);
    } else if (!wzdControl.nextPageHref) {
      o.msg = `Não está definido o próximo passo para seleção múltipla.`;
    } else if (k == (i = wzdControl.getSelectedCount())) {
      return true;
    } else if (k == 1) { // Um grupo somente
      o.msg = `Por favor, selecione uma das opções do grupo.`;
    } else {
      o.msg = `Por favor, selecione uma opção de cada um dos ${k} grupos`;
      const f = k - i;
      o.msg += (i == 0) ? '.' : ` (falta${(f == 1) ? ' um' : `m ${f}`}).`;
    }
    return false;
  },

  /** @private */
  gotoNextPage: () => {
    let sHref = '';
    let jsBtn
    let o = { msg: '' };
    if (wzdControl.fOnNext && !wzdControl.fOnNext()) {
      // Not this time 8-|
    } else if (wzdControl.displayMode == wzdControl.mode.CUSTOM) {
      sHref = wzdControl.nextPageHref;
    } else if (wzdControl.jsoData.length == 0) {
      wzdControl.messageError(`Não exitem items para selecionar.`)
    } else if (!wzdControl.selectionReady(o)) {
      wzdControl.messageInfo(o.msg)
    } else if (wzdControl.multiSelect) {
      const sIds = wzdControl.groups.map(grp => wzdControl.jsoData[grp.selected].id).join('-');
      sHref = `${wzdControl.nextPageHref}?id=${sIds}`;
    } else if ((jsBtn = wzdControl.jsoData[wzdControl.selectedItemIx]).href) {
      sHref = jsBtn.href;
    } else if (!wzdControl.nextPageHref) {
      wzdControl.messageError(`Não está definido o próximo passo de '${jsBtn.caption}'.`)
    } else if (jsBtn.id) {
      sHref = `${wzdControl.nextPageHref}?id=${jsBtn.id}`;
    } else {
      sHref = jsBtn.href || wzdControl.nextPageHref;
    }
    if (sHref) setTimeout(() => { window.location.href = sHref }, 0);
  },

  /** @public */
  messageInfo: (sMsg, sTitle) => {
    if (wzdControl.modalReady()) {
      // @ts-ignore mdlControl
      mdlControl.message(sMsg, sTitle)
    } else {
      alert(sMsg)
    }
  },

  /** @public */
  messageError: (sMsg, sTitle, fOnError) => {
    if (fOnError) { fOnError(); }
    if (wzdControl.modalReady()) {
      // @ts-ignore mdlControl
      mdlControl.messageError(sMsg, sTitle)
    } else {
      wzdControl.messageInfo(sMsg, sTitle)
    }
  },

  /**
   * Return the text of the selected option of the param
   * @param {HTMLSelectElement} eleSelect
   * @returns {string}
   * @public
   */
  getSelectedTextFrom: (eleSelect) => {
    let sText = '';
    if (eleSelect && eleSelect.selectedIndex >= 0) {
      sText= eleSelect.options[eleSelect.selectedIndex].text;
    }
    return sText;
  },

  /**
   * Display HTML text of selected item
   * @param {string} sHtml
   * @public
   */
  displaySelected: (sHtml) => {
    const eleUsDisplay = wzdControl.ge('idWzdUsDisplay');
    eleUsDisplay.innerHTML = '' + sHtml;
    if (sHtml) {
      eleUsDisplay.classList.remove('visually-hidden');
    } else {
      eleUsDisplay.classList.add('visually-hidden');
    }
  },

  /**
   * @enum {number} Wizard items display mode
   * @public
  */
  mode: { BUTTONS: 1, IMAGES: 2, CUSTOM: 3 },

  /**
   * Initialize wizard's page
   * @param {wzdConfig} jsonConfig
   * @public
   */
  initPage: (jsonConfig) => {
    wzdControl.jsoData = jsonConfig.data || [];
    wzdControl.displayMode = jsonConfig.mode;
    wzdControl.fOnNext = jsonConfig.onNext || null;
    wzdControl.nextPageHref = (jsonConfig.nextPage || '').trim();
    wzdControl.path = (jsonConfig.path || '../../static/assets/img/wizard/').trim();
    wzdControl.multiSelect = jsonConfig.multiSelect || false;
    wzdControl.alignText = jsonConfig.alignText || 'center';
    if (!wzdControl.path.endsWith('/')) wzdControl.path += '/';
    wzdControl.display();
    // don't use try catch, if an error occurs, better leave button disabled
    /** @type {HTMLButtonElement} */ (wzdControl.ge('idWzdBtnOk')).disabled = false;
  },

}
//{# eof #}