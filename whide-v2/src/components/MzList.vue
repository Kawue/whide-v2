<template>
  <div class="mzComp" id="mzComponent">
      <div>MZs</div>
      <span
        style="float: left;margin-left: 30px; color: white"
        v-on:click="toggleShowAnnotation"
        v-b-tooltip.hover.top="'Show Annotations'"
      >
          <v-icon
            name="pencil-alt"
          ></v-icon>
        </span>
      <span
        v-on:click="toggleAsc(), sortMZ()"
        style="float: right; margin-right: 30px; padding: 2px; color :white"
        v-b-tooltip.hover.top="'Sort'"
      >
        <v-icon
          v-bind:name="asc ? 'sort-amount-up' : 'sort-amount-down'"
        ></v-icon>
        </span>
      <select class="list" id="mzlistid" multiple>
        <option
          v-for="(key, val) in mzObjects"
          v-bind:key="key"
          v-bind:value="key"
          v-on:dblclick="annotateMzItem(val, key)"
            >
          {{showAnnotation ? key : val}} <!--first mzItem is the name-->
        </option>
      </select>

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
              <label for="annotation-input">Annotation:</label>
            </b-col>
            <b-col sm="9">
              <b-form ref="form" @submit.stop.prevent="handleSubmit">
                <b-input
                  v-model="nameModalMz.name"
                  placeholder="MZ Name"
                  required
                  maxlength="30"
                  :state="nameModalMz.name.length > 0 ? null : false"
                  id="annotation-input"
                  trim
                  ref="annotationinput"
                ></b-input>
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

export default {
  name: 'mzlist',
  data: function () {
    return {
      localSelectedMz: [],
      nameModalMz: {
        name: '',
        mzValue: 0
      }
    };
  },
  computed: {
    ...mapGetters({
      mzObjects: 'getMzObject',
      mzAnnotations: 'getMzAnnotations',
      showAnnotation: 'mzShowAnnotation',
      asc: 'mzAsc',
      height: 'getMzHeight'
    })
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
    }
  },
  created () {
    store.commit('SET_MZ_OBJECT');
  }

};

</script>
<style scoped lang="scss">
  .mzComp {
    height: 100vh;
  }
  .list {
    padding: 0;
    font-size: 0.9em;
    height: 93%;
    width: 100%;
    text-align: center;
    margin-top: 8px;
  }
  .options {
    background-color: darkgray;
  }
  .v-icon {
    color: white;
  }
</style>
