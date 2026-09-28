/* ELLASTORE frontend entry: shared components + the current page's module. */
import { $ } from './lib/dom.js';
import { initHeader } from './components/header.js';
import { initSubscribe } from './components/subscribe.js';
import { initHome } from './pages/home.js';
import { initTopup } from './pages/topup.js';

initHeader();
initSubscribe();

const page = document.body.dataset.page;
if (page === 'home') initHome();
if (page === 'topup') initTopup($('[data-topup]'));
