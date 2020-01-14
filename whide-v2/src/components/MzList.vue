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
      <span
        class="mzButtonLine"
        v-on:click="addMzToAggregationList"
        v-b-tooltip.hover.top="'Focused MZ-Value to Aggregation List'"
      >
          <v-icon
            name="arrow-up" style="color: orange"
          />
        </span>
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
      <select class="listMz" id="listForMzImage" multiple v-on:focus="setAggregationFocus" v-on:focusout="changeFocus">

      </select>
    <label id="mzListLabel" for="mzlistid"/>
    <select class="list" id="mzlistid" multiple v-on:focus="setListFocus" v-on:focusout="changeFocus" >
      <option
        style="color: white"
        v-for="(key, val) in mzObjects"
        v-bind:key="key"
        v-bind:value="key"
        v-bind:id="val.toString()"
        v-on:click="clickChecker($event, val, key)"
      >
        {{showAnnotation ? key : val}} <!--first mzItem is the name-->
      </option>
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
            <label for="annotationinput">Annotation:</label>
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
      aggregationList: [],
      aggregationListGrey: [],
      delay: 190,
      clicks: 0,
      aggregationClicks: 0,
      timer: null,
      currentMzValueToAdd: [],
      currentMzValueToRemove: null
    };
  },
  computed: {
    ...mapGetters({
      mzObjects: 'getMzObject',
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
        let newHeight = this.windowHeight - parseInt(this.height) - 50;
        d3.select('#selectionContainer')
          .style('height', newHeight + 'px');
        d3.select('#mzlistid').style('height', newHeight / 2 + 'px');
        d3.select('#listFormzImage').style('height', newHeight / 2 + 'px');
      }
      if (mutation.type === 'SET_FOCUS_MZ_LIST') {
        if (!this.focusMzList) {
          let mzListId = document.querySelector('#mzlistid');
          mzListId.removeEventListener('change', this.showSingleImage);
          mzListId.removeEventListener('keydown', this.chooseKey);
          let aggregationList = document.querySelector('#listForMzImage');
          aggregationList.removeEventListener('keydown', this.chooseKeyAggregation);
          aggregationList.removeEventListener('change', this.setMzValueToRemove);
        }
      }
      if (this.firstBuild) {
        let height = this.windowHeight - 40;
        d3.select('#selectionContainer')
          .style('height', height - 50 + 'px');
        this.firstBuild = false;
      }
    });
  },
  methods: {
    changeFocus: function () {
      store.commit('SET_FOCUS_MZ_LIST', false);
    },
    setListFocus: function () {
      store.commit('SET_FOCUS_MZ_LIST', true);
      let that = this;
      let mzList = document.querySelector('#mzlistid');
      mzList.addEventListener('change', function (e) {
        let arrayOfSelecedIDs = [];
        let elements = document.getElementById(this.id).childNodes;
        for (let i = 0; i < elements.length; i++) {
          if (elements[i].selected) {
            arrayOfSelecedIDs.push(elements[i].value);
          }
        }
        that.currentMzValueToAdd = Array.from(arrayOfSelecedIDs);
        if (arrayOfSelecedIDs.length === 1) {
          that.showSingleImage(this.value);
        }
      });
      mzList.addEventListener('keydown', function (event) {
        let key = event.keyCode;
        that.chooseKey(that.currentMzValueToAdd, key);
      });
    },
    setAggregationFocus: function () {
      store.commit('SET_FOCUS_MZ_LIST', true);
      let that = this;
      let listForMzImage = document.querySelector('#listForMzImage');
      listForMzImage.addEventListener('keydown', function (event) {
        let key = event.keyCode;
        that.chooseKeyAggregation(this.value, key);
      });
      listForMzImage.addEventListener('change', function () {
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
      var mzToAnnotate = [this.nameModalMz.mzValue, this.nameModalMz.name];
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
      var mzResetting = [this.nameModalMz.mzValue, this.nameModalMz.mzValue];
      store.commit('SET_MZ_ANNOTATION', mzResetting);
    },
    addMzItem: function (val) {
      let that = this;
      if (!this.aggregationList.includes(val)) {
        let height = d3.select('#listForMzImage').node().getBoundingClientRect().height + 22;
        let mzListHeight = d3.select('#mzlistid').node().getBoundingClientRect().height - 22;
        if (height <= mzListHeight) {
          d3.select('#listForMzImage')
            .style('height', height + 'px')
            .append('option')
            .text(val)
            .style('color', 'white')
            .attr('id', val.toString())
            .on('click', function () {
              that.greyMzItem(val);
            });
          d3.select('#mzlistid').style('height', mzListHeight + 'px');
        } else {
          d3.select('#listForMzImage')
            .append('option')
            .text(val)
            .style('color', 'white')
            .attr('id', val.toString())
            .on('click', function () {
              that.greyMzItem(val);
            });
        }
        this.aggregationList.push(val);
      }
    },
    addMzToAggregationList: function () {
      let that = this;
      this.currentMzValueToAdd.forEach(function (item) {
        that.addMzItem(parseFloat(item));
      });
    },
    greyMzItem: function (mzItem) {
      if (this.aggregationList.includes(mzItem)) {
        d3.select('[id="' + mzItem.toString() + '"]').style('color', 'grey');
        for (let i = 0; i < this.aggregationList.length; i++) {
          if (this.aggregationList[i] === mzItem) {
            this.aggregationList.splice(i, 1);
          }
        }
        this.aggregationListGrey.push(mzItem);
      } else {
        d3.select('[id="' + mzItem.toString() + '"]').style('color', 'white');
        for (let i = 0; i < this.aggregationListGrey.length; i++) {
          if (this.aggregationListGrey[i] === mzItem) {
            this.aggregationListGrey.splice(i, 1);
          }
        }
        this.aggregationList.push(mzItem);
      }
      this.currentMzValueToRemove = mzItem;
    },

    removeMzFromAggregationList: function () {
      const item = parseFloat(this.currentMzValueToRemove);
      d3.select('[id="' + item.toString() + '"]').remove();
      const height = d3.select('#listForMzImage').node().getBoundingClientRect().height - 22;
      d3.select('#listForMzImage').style('height', height + 'px');
      if (this.aggregationList.includes(item)) {
        for (let i = 0; i < this.aggregationList.length; i++) {
          if (this.aggregationList[i] === item) {
            this.aggregationList.splice(i, 1);
          }
        }
      } else {
        for (let i = 0; i < this.aggregationListGrey.length; i++) {
          if (this.aggregationListGrey[i] === item) {
            this.aggregationListGrey.splice(i, 1);
          }
        }
      }
    },
    showSingleImage: function (mzItem) {
      const mzList = [mzItem];
      this.currentMzValueToAdd = mzList;
      store.commit('SET_NEW_MZ_VALUE', mzList);
      store.dispatch('fetchImageData');
    },
    chooseKey: function (mzItem, key) {
      let that = this;
      if (key === 13) {
        mzItem.forEach(function (item) {
          that.addMzItem(parseFloat(item));
        });
      } else if (key === 46) {
        console.log('removeMzList');
      }
    },
    chooseKeyAggregation: function (mzItem, key) {
      if (key === 13) {
        this.greyMzItem(parseFloat(mzItem));
      } else if (key === 46) {
        this.removeMzFromAggregationList();
      }
    },
    clickChecker: function (event, val, key) {
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
        this.annotateMzItem(val, key);
        this.clicks = 0;
      }
    },
    clickCheckerAggregation: function (event, val, key) {
      this.aggregationClicks++;
      if (this.aggregationClicks === 1) {
        var self = this;
        this.timer = setTimeout(function () {
          this.greyMzItem(val);
          self.aggregationClicks = 0;
        }, this.delay);
      } else {
        clearTimeout(this.timer);
        this.annotateMzItem(val, key);
        this.aggregationClicks = 0;
      }
    },
    clearAggregationList: function () {
      d3.select('#listForMzImage')
        .style('height', 0)
        .selectAll('*').remove();
      this.aggregationList = [];
      this.aggregationListGrey = [];
    },
    showMzImageAggregationList: function () {
      store.commit('SET_NEW_MZ_VALUE', this.aggregationList);
      store.dispatch('fetchImageData');
    },
    setMzValueToRemove: function (mzItem) {
      this.currentMzValueToRemove = mzItem;
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
  .list {
    padding: 0;
    font-size: 0.9em;
    width: 100%;
    text-align: center;
    margin-top: 8px;
    height: 96%;
    background-color: #4f5051;
  }
  .listMz {
    padding: 0;
    font-size: 0.9em;
    width: 100%;
    height: 22px;
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
  }
  .mzButtonLine {
    color: white;
  }
</style>
