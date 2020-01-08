<template>
  <div class="mzComp" id="mzComponent">
    <div style="color: white">MZs</div>
    <span
      style="float: left;margin-left: 30px; color: white"
      v-on:click="toggleShowAnnotation"
      v-b-tooltip.hover.top="'Show Annotations'"
    >
          <v-icon
            name="pencil-alt" style="color: orange"
          />
        </span>
    <span
      style="align: center; color: white"
      v-on:click="toggleMzImage"
      v-b-tooltip.hover.top="'mark Values for MZ-Image'">
      <v-icon
        v-bind:name="markForMzImage ? 'pause' : 'play'" style="color: orange"/>
    </span>
    <span
      v-on:click="toggleAsc(), sortMZ()"
      style="float: right; margin-right: 30px; padding: 2px; color :white"
      v-b-tooltip.hover.top="'Sort'"
    >
        <v-icon
          v-bind:name="asc ? 'sort-amount-up' : 'sort-amount-down'" style="color: orange"
        />
        </span>
    <div id="selectionContainer">
    <label id="mzListLabel" for="mzlistid"/>
    <select class="list" id="mzlistid" multiple>
      <option
        style="color: white"
        v-for="(key, val) in mzObjects"
        v-bind:key="key"
        v-bind:value="key"
        v-bind:id="val.toString()"
        v-on:dblclick="annotateMzItem(val, key)"
        v-on:click="addMzItem(key)"
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
      markForMzImage: false,
      localSelectedMz: []

    };
  },
  computed: {
    ...mapGetters({
      mzObjects: 'getMzObject',
      mzAnnotations: 'getMzAnnotations',
      showAnnotation: 'mzShowAnnotation',
      asc: 'mzAsc',
      height: 'getBottonBarHeight'
    })
  },
  mounted () {
    store.subscribe(mutation => {
      if (mutation.type === 'SET_BOTTOMBAR_HEIGHT') {
        let newHeight = this.windowHeight - parseInt(this.height);
        d3.select('.list')
          .style('height', newHeight - 90 + 'px');
      }
      if (this.firstBuild) {
        let height = this.windowHeight - 40;
        d3.select('.list')
          .style('height', height - 90 + 'px');
        this.firstBuild = false;
      }
    });
  },
  methods: {
    toggleAsc: function () {
      store.commit('MZLIST_TOOGLE_ASC');
    },
    sortMZ: function () {
      store.commit('MZLIST_SORT_MZ');
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
    },
    handleCancle: function () {
      var mzResetting = [this.nameModalMz.mzValue, this.nameModalMz.mzValue];
      store.commit('SET_MZ_ANNOTATION', mzResetting);
    },
    toggleMzImage: function () {
      this.markForMzImage = !this.markForMzImage;
      if (this.markForMzImage === true) {
        d3.select('#selectionContainer')
          .append('select')
          .attr('id', 'listMzImage')
          .style('padding', 0)
          .style('font-size', '0.9em')
          .style('width', '100%')
          .style('text-align', 'center')
          .style('background-color', '#4f5051');
      } else {
        d3.select('#listMzImage').remove();
      }
    },
    addMzItem: function (val) {
      if (!this.localSelectedMz.includes(parseFloat(val))) {
        this.localSelectedMz.push(val);
        const sendPackage = {
          add: true,
          mzValue: parseFloat(val)
        };
        store.commit('SET_NEW_MZ_VALUE', sendPackage);
        this.localSelectedMz.push(parseFloat(val));
      } else {
        const sendPackage = {
          add: false,
          mzValue: parseFloat(val)
        };
        store.commit('SET_NEW_MZ_VALUE', sendPackage);
        for (var i = 0; i < this.localSelectedMz.length; i++) {
          if (this.localSelectedMz[i] === parseFloat(val)) {
            this.localSelectedMz.splice(i, 1);
          }
        }
      }
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
    background-color: #4f5051;
  }
  .listMz {
    padding: 0;
    font-size: 0.9em;
    width: 100%;
    text-align: center;
    background-color: #4f5051;
  }
  .options {
    background-color: darkgray;
  }
</style>
