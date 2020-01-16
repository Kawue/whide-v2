<template>
  <div class="mzComp" id="mzComponent">
    <div class="button-area-line">
      <span
        class="mzButtonLine"
        v-on:click="toggleShowAnnotation"
        v-b-tooltip.hover.top="'Show Annotations'"
      >
          <v-icon
            name="pencil-alt" style="color: orange"
          />
        </span>
      <div class="vl"/>
      <span
        class="mzButtonLine"
        v-on:click="addMzToAggregationList"
        v-b-tooltip.hover.top="'Focused MZ-Value to Aggregation List'"
      >
          <v-icon
            name="arrow-up" style="color: orange"
          />
        </span>
      <div class="vl"/>
      <span
        class="mzButtonLine"
        v-on:click="removeMzFromAggregationList"
        v-b-tooltip.hover.top="'Remove MZ-Values from Aggregation List'"
      >
          <v-icon
            name="arrow-down" style="color: orange"
          />
        </span>
      <span
        class="mzButtonLine"
        v-on:click="clearAggregationList"
        v-b-tooltip.hover.top="'Remove all MZ-Values from Aggregation List'"
      >
          <v-icon
            name="broom" style="color: orange"
          />
        </span>
      <span
        class="mzButtonLine"
        v-on:click="showMzImageAggregationList"
        v-b-tooltip.hover.top="'Show MZ-Image from Aggregation List'"
      >
          <v-icon
            name="sign-in-alt" style="color: orange"
          />
        </span>
    </div>
    <div id="selectionContainer">
      <label for="mzValueAggregationList"/>
      <select class="listMz" id="mzValueAggregationList" multiple v-on:focus="setAggregationFocus" v-on:focusout="changeFocus">

      </select>
    <label id="mzListLabel" for="mzValueList"/>
    <select class="list" id="mzValueList" multiple v-on:focus="setListFocus" v-on:focusout="changeFocus" >
    </select>
    </div>
    <b-modal
      id="nameModal"
      ref="nameModal"
      @ok="submitAnnotation"
      @cancel="handleCancle"
      title="Rename m/z Value"
    >
      <template slot="default">
        <b-row>
          <b-col sm="3" class="align-self-center">
            <p>m/z Value:</p>
          </b-col>
          <b-col sm="9">
            <p id="annotation-mz-value">{{ nameModalMz.mzValue }}</p>
          </b-col>
          <b-col sm="3" class="align-self-center">
            <label>Annotation:</label>
          </b-col>
          <b-col sm="9">
            <b-form ref="form" @submit.stop.prevent="handleSubmit">
              <b-input
                v-model="nameModalMz.name"
                placeholder="MZ Name"
                required
                maxlength="30"
                :state="nameModalMz.name.length > 0 ? null : false"
                id="annotationinput"
                trim
                ref="annotationinput"
              />
            </b-form>
          </b-col>
        </b-row>
        <b-row>
          <b-col offset-sm="3">
            <b-form-invalid-feedback
              :state="nameModalMz.name.length > 0 ? null : false"
            >
              The Annotation can't be empty
            </b-form-invalid-feedback>
          </b-col>
        </b-row>
      </template>
      <template
        slot="modal-footer"
        style="display: block !important;"
        slot-scope="{ cancel, ok }"
      >
        <b-button
          variant="outline-danger"
          @click="cancel()"
          v-bind:disabled="nameModalMz.mzValue === nameModalMz.name"
        >
          Reset
        </b-button>
        <b-button
          variant="success"
          @click="ok()"
          v-bind:disabled="nameModalMz.name.length === 0"
        >
          Save
        </b-button>
      </template>
    </b-modal>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import store from '../store';
import * as d3 from 'd3';

export default {
  name: 'mzlist',
  data: function () {
    return {
      nameModalMz: {
        name: '',
        mzValue: 0
      },
      windowHeight: document.documentElement.clientHeight,
      firstBuild: true,
      aggregationList: {},
      aggregationListGrey: {},
      delay: 190,
      clicks: 0,
      aggregationClicks: 0,
      timer: null,
      selectedMzValues: [],
      selectedAggregationValues: null,
      ignoreList: {},
      currentMzObject: {}
    };
  },
  computed: {
    ...mapGetters({
      mzObject: 'getMzObject',
      mzAnnotations: 'getMzAnnotations',
      showAnnotation: 'mzShowAnnotation',
      height: 'getBottonBarHeight',
      focusMzList: 'getFocusMzList'
    })
  },
  mounted () {
    // TODO fix bottombar height adjustmentg
    store.subscribe(mutation => {
      if (mutation.type === 'SET_BOTTOMBAR_HEIGHT') {
        const newHeight = this.windowHeight - parseInt(this.height) - 50;
        d3.select('#selectionContainer')
          .style('height', newHeight + 'px');
      }
      if (mutation.type === 'SET_FOCUS_MZ_LIST') {
        if (!this.focusMzList) {
          let mzListId = document.querySelector('#mzValueList');
          mzListId.removeEventListener('change', this.showSingleImage);
          mzListId.removeEventListener('keydown', this.chooseKey);
          let aggregationList = document.querySelector('#mzValueAggregationList');
          aggregationList.removeEventListener('keydown', this.chooseKeyAggregation);
          aggregationList.removeEventListener('change', this.setMzValueToRemove);
        }
      }
      if (mutation.type === 'MZLIST_SHOW_ANNOTATIONS') {
        this.renderAggregationList();
        this.renderMzList(this.currentMzObject, 'white');
        this.renderMzList(this.ignoreList, 'grey');
      }
      if (this.firstBuild) {
        let height = this.windowHeight - 40;
        d3.select('#selectionContainer')
          .style('height', height - 50 + 'px');
        this.firstBuild = false;
      }
    });
    this.currentMzObject = Object.assign({}, this.mzObject);
    this.renderMzList(this.currentMzObject, 'white');
  },
  methods: {
    changeFocus: function () {
      store.commit('SET_FOCUS_MZ_LIST', false);
    },
    setListFocus: function () {
      store.commit('SET_FOCUS_MZ_LIST', true);
      let that = this;
      let mzList = document.querySelector('#mzValueList');
      mzList.addEventListener('change', function (e) {
        let arrayOfSelecedIDs = [];
        let elements = document.getElementById(this.id).childNodes;
        for (let i = 0; i < elements.length; i++) {
          if (elements[i].selected) {
            arrayOfSelecedIDs.push(elements[i].id);
          }
        }
        that.selectedMzValues = Array.from(arrayOfSelecedIDs);
        if (arrayOfSelecedIDs.length === 1) {
          that.showSingleImage(arrayOfSelecedIDs[0]);
        }
      });
      mzList.addEventListener('keydown', function (event) {
        let key = event.keyCode;
        that.chooseKey(that.selectedMzValues, key);
      });
    },
    setAggregationFocus: function () {
      store.commit('SET_FOCUS_MZ_LIST', true);
      let that = this;
      let aggreList = document.querySelector('#mzValueAggregationList');
      aggreList.addEventListener('keydown', function (event) {
        let key = event.keyCode;
        that.chooseKeyAggregation(this.value, key);
      });
      aggreList.addEventListener('change', function () {
        that.setMzValueToRemove(this.value);
      });
    },
    toggleShowAnnotation: function () {
      store.commit('MZLIST_SHOW_ANNOTATIONS');
    },
    annotateMzItem: function (mzKey, mzVal) {
      this.nameModalMz = {
        mzValue: mzKey,
        name: mzVal
      };
      this.$refs['nameModal'].show();
      setTimeout(() => {
        this.$refs['annotationinput'].focus();
      }, 500);
    },
    submitAnnotation: function (bvModalEvt) {
      bvModalEvt.preventDefault();
      this.handleSubmit();
    },
    handleSubmit: function () {
      if (!this.$refs.form.checkValidity()) {
        return;
      }
      let mzToAnnotate = [this.nameModalMz.mzValue, this.nameModalMz.name];
      if (this.nameModalMz.mzValue.toString() in this.aggregationList) {
        this.aggregationList[this.nameModalMz.mzValue.toString()] = this.nameModalMz.name;
      } else if (this.nameModalMz.mzValue.toString() in this.aggregationListGrey) {
        this.aggregationListGrey[this.nameModalMz.mzValue.toString()] = this.nameModalMz.name;
      }
      if (this.nameModalMz.mzValue.toString() in this.currentMzObject) {
        this.currentMzObject[this.nameModalMz.mzValue.toString()] = this.nameModalMz.name;
      } else if (this.nameModalMz.mzValue.toString() in this.ignoreList) {
        this.ignoreList[this.nameModalMz.mzValue.toString()] = this.nameModalMz.name;
      }
      this.renderAggregationList();
      this.renderMzList(this.currentMzObject, 'white');
      this.renderMzList(this.ignoreList, 'grey');

      store.commit('SET_MZ_ANNOTATION', mzToAnnotate);

      this.$nextTick(() => {
        this.$refs['nameModal'].hide();
      });
      setTimeout(() => {
        this.nameModalMz = {
          name: '',
          mzValue: 0
        };
      }, 1000);
      store.commit('SET_FOCUS_MZ_LIST', true);
    },
    handleCancle: function () {
      let mzResetting = [this.nameModalMz.mzValue, this.nameModalMz.mzValue];
      if (this.nameModalMz.mzValue.toString() in this.aggregationList) {
        this.aggregationList[this.nameModalMz.mzValue.toString()] = this.nameModalMz.mzValue;
      }
      store.commit('SET_MZ_ANNOTATION', mzResetting);
    },
    addMzItem: function (val, annotation) {
      let that = this;
      if (!(val in this.aggregationList)) {
        this.adjustHeight(true);
        this.aggregationList[val] = annotation;
        that.renderAggregationList();
      }
    },
    addMzToAggregationList: function () {
      let that = this;
      this.selectedMzValues.forEach(function (item) {
        that.addMzItem(parseFloat(item), that.mzObject[item]);
      });
    },
    greyMzItem: function (mzItem) {
      if (mzItem in this.aggregationList) {
        d3.select('[id="' + 'aggregation_' + mzItem.toString() + '"]').style('color', 'grey');
        this.aggregationListGrey[mzItem] = this.aggregationList[mzItem];
        delete this.aggregationList[mzItem];
      } else {
        d3.select('[id="' + 'aggregation_' + mzItem.toString() + '"]').style('color', 'white');
        this.aggregationList[mzItem] = this.aggregationListGrey[mzItem];
        delete this.aggregationListGrey[mzItem];
      }
      this.selectedAggregationValues = mzItem;
    },

    removeMzFromAggregationList: function () {
      const item = parseFloat(this.selectedAggregationValues);
      d3.select('[id="' + 'aggregation_' + item.toString() + '"]').remove();
      this.adjustHeight(false);
      if (item in this.aggregationList) {
        delete this.aggregationList[item];
      } else {
        delete this.aggregationListGrey[item];
      }
    },
    showSingleImage: function (mzItem) {
      const mzList = [mzItem];
      this.selectedMzValues = mzList;
      store.commit('SET_NEW_MZ_VALUE', mzList);
      store.dispatch('fetchImageData');
    },
    chooseKey: function (mzItem, key) {
      let that = this;
      if (key === 13) {
        mzItem.forEach(function (item) {
          that.addMzItem(parseFloat(item), that.mzObject[item]);
        });
      } else if (key === 46) {
        mzItem.forEach(function (item) {
          if (item in that.ignoreList) {
            that.currentMzObject[item] = that.mzObject[item];
            delete that.ignoreList[item];
          } else {
            that.ignoreList[item] = that.mzObject[item];
            delete that.currentMzObject[item];
          }
        });
        that.renderMzList(this.currentMzObject, 'white');
        that.renderMzList(this.ignoreList, 'grey');
      }
    },
    chooseKeyAggregation: function (mzItem, key) {
      if (key === 13) {
        this.greyMzItem(parseFloat(mzItem));
      } else if (key === 46) {
        this.removeMzFromAggregationList();
      }
    },
    clickChecker: function (event, val, annotation) {
      this.clicks++;
      if (this.clicks === 1) {
        var self = this;
        this.timer = setTimeout(function () {
          self.showSingleImage(val);
          self.clicks = 0;
          store.commit('SET_FOCUS_MZ_LIST', true);
        }, this.delay);
      } else {
        clearTimeout(this.timer);
        this.annotateMzItem(val, annotation);
        this.clicks = 0;
      }
    },
    clickCheckerAggregation: function (event, val, annotation) {
      this.aggregationClicks++;
      if (this.aggregationClicks === 1) {
        let self = this;
        this.timer = setTimeout(function () {
          self.greyMzItem(val);
          self.aggregationClicks = 0;
        }, this.delay);
      } else {
        clearTimeout(this.timer);
        this.annotateMzItem(val, annotation);
        this.aggregationClicks = 0;
      }
    },
    clearAggregationList: function () {
      d3.select('#mzValueAggregationList')
        .selectAll('*').remove();
      this.aggregationListGrey = {};
      this.aggregationList = {};
    },
    showMzImageAggregationList: function () {
      store.commit('SET_NEW_MZ_VALUE', Object.keys(this.aggregationList));
      store.dispatch('fetchImageData');
    },
    setMzValueToRemove: function (mzItem) {
      this.selectedAggregationValues = mzItem;
    },
    renderAggregationList: function () {
      let that = this;
      let combinedList;
      d3.select('#mzValueAggregationList')
        .selectAll('*').remove();
      combinedList = Object.keys(this.aggregationList).concat(Object.keys(this.aggregationListGrey));
      combinedList.sort(function (a, b) {
        return a - b;
      });
      if (this.showAnnotation) {
        combinedList.forEach(function (mzKey) {
          d3.select('#mzValueAggregationList')
            .append('option')
            .text(that.aggregationList[mzKey])
            .style('color', 'white')
            .attr('id', 'aggregation_' + mzKey.toString())
            .on('click', function (event) {
              that.clickCheckerAggregation(event, mzKey, that.aggregationList[mzKey]);
            });
          if (mzKey in that.aggregationListGrey) {
            d3.select('[id="' + 'aggregation_' + mzKey.toString() + '"]').style('color', 'grey');
          }
        });
      } else {
        combinedList.forEach(function (mzKey) {
          d3.select('#mzValueAggregationList')
            .append('option')
            .text(mzKey)
            .style('color', 'white')
            .attr('id', 'aggregation_' + mzKey.toString())
            .on('click', function (event) {
              that.clickCheckerAggregation(event, mzKey, that.aggregationList[mzKey]);
            });
          if (mzKey in that.aggregationListGrey) {
            d3.select('[id="' + 'aggregation_' + mzKey.toString() + '"]').style('color', 'grey');
          }
        });
      }
    },
    renderMzList: function (dict, color) {
      // console.log(dict);
      let that = this;
      let sortingList = Object.keys(dict);
      sortingList.sort(function (a, b) {
        return a - b;
      });

      sortingList.forEach(function (item) {
        d3.select('[id="' + item.toString() + '"]').remove();
        if (that.showAnnotation) {
          d3.select('#mzValueList')
            .append('option')
            .attr('id', item)
            .text(dict[item].toString())
            .on('click', function (event) {
              that.clickChecker(event, item, dict[item]);
            })
            .style('color', color);
        } else {
          d3.select('#mzValueList')
            .append('option')
            .attr('id', item.toString())
            .text(item.toString())
            .on('click', function (event) {
              that.clickChecker(event, item, dict[item]);
            })
            .style('color', color);
        }
      });
    },
    adjustHeight: function (addOrRemove) {
      let maxHeight = d3.select('#selectionContainer').node().getBoundingClientRect().height;
      let aggregationHeight = d3.select('#mzValueAggregationList').node().getBoundingClientRect().height;
      let mzListHeight = d3.select('#mzValueList').node().getBoundingClientRect().height;
      let percent = maxHeight / 100;
      let newAggreHeight;
      let newMzListHeight;
      if (addOrRemove) {
        newAggreHeight = (aggregationHeight / percent) + 2;
        newMzListHeight = (mzListHeight / percent) - 2;
      } else {
        newAggreHeight = (aggregationHeight / percent) - 2;
        newMzListHeight = (mzListHeight / percent) + 2;
      }

      d3.select('#mzValueAggregationList').style('height', newAggreHeight + '%');
      d3.select('#mzValueList').style('height', newMzListHeight + '%');
    }
  },
  created () {
    store.commit('SET_MZ_OBJECT');
  }

};

</script>
<style scoped lang="scss">
  .mzComp {
    top: 0;
  }
  #selectionContainer {
    height: 80vh;
  }
  .list {
    padding: 0;
    font-size: 0.95em;
    width: 100%;
    text-align: center;
    margin-top: 8px;
    height: 91%;
    max-height: 93%;
    background-color: #4f5051;
  }
  .listMz {
    padding: 0;
    font-size: 0.95em;
    width: 100%;
    height: 4%;
    min-height: 4%;
    text-align: center;
    background-color: #4f5051;
  }
  .options {
    background-color: darkgray;
  }
  .button-area-line {
    margin: 2px auto;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    flex-wrap: nowrap;
    max-width: 90%;
    height: 3vh;
  }
  .mzButtonLine {
    color: white;
  }
  .vl {
    border-left: 1px solid orange;
    height: 3vh;
  }
</style>
